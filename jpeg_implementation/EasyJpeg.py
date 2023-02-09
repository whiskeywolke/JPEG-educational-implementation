import os.path
import time

import numpy as np
from matplotlib import pyplot as plt

from jpeg_implementation.dct import block_dct2, block_idct2
from jpeg_implementation.huffman import generate_huffman_code, encode_huffman, decode_huffman
from jpeg_implementation.quantization import quantization_tables, quantize, quantize_inverse
from jpeg_implementation.rgbToYuv import rgb_to_yuv, yuv_to_rgb
from jpeg_implementation.runLengthEncode import resort_and_run_length_encode, unsort_and_run_length_decode
from jpeg_implementation.serialize import image_data_to_bytes, bytes_to_image_data
from jpeg_implementation.splitBlocks import split, merge_blocks
from jpeg_implementation.subsample import subsample_u_v, calculate_down_sampled_resolution, up_sample_u_v


class EasyJpeg:
    original_file_name = None

    original_image = None
    decompressed_image = None

    compressed_byte_data = None
    compression_ratio = None

    compression_time = None
    compression_time_details = None

    decompression_time = None
    decompression_time_details = None

    def __init__(self, filename, original_image, decompressed_image, compressed_byte_data, compression_ratio,
                 compression_time, compression_time_details, decompression_time, decompression_time_details):
        self.original_file_name = filename
        self.original_image = original_image
        self.decompressed_image = decompressed_image
        self.compressed_byte_data = compressed_byte_data
        self.compression_ratio = compression_ratio
        self.compression_time = compression_time
        self.compression_time_details = compression_time_details
        self.decompression_time = decompression_time
        self.decompression_time_details = decompression_time_details

    def set_original_image(self, path):
        self.original_image = EasyJpeg.read_original_image(path)

    @staticmethod
    def read_original_image(path):
        original_image = plt.imread(path)
        # strip alpha channel if exists
        if original_image.shape[2] == 4:
            channels = np.dsplit(original_image, 4)
            original_image = np.dstack(channels[:3])
        return original_image

    @staticmethod
    def from_png(path, quantization_table_quality, subsampling_settings, block_size=8):
        original_image = EasyJpeg.read_original_image(path)

        original_size = os.path.getsize(path)
        compressed_byte_data, compression_time, compression_times_detail = EasyJpeg.__compress(original_image,
                                                                                               quantization_table_quality,
                                                                                               subsampling_settings,
                                                                                               block_size)
        decompressed_image, decompression_time, decompression_time_detail = EasyJpeg.__decompress(compressed_byte_data)
        compression_ratio = original_size / len(compressed_byte_data)

        return EasyJpeg(path, original_image, decompressed_image, compressed_byte_data, compression_ratio,
                        compression_time, compression_times_detail, decompression_time, decompression_time_detail)

    @staticmethod
    def from_compressed(path):
        with open(path, "rb") as fp:
            data = fp.read()
            decompressed_image, decompression_time, decompression_time_detail = EasyJpeg.__decompress(data)
            return EasyJpeg(None, None, decompressed_image, data, None, None, None,
                            decompression_time, decompression_time_detail)

    @staticmethod
    def __compress(original_image, quantization_table_quality, subsampling_settings, block_size):
        t0 = time.time()
        original_image_resolution = tuple(reversed(original_image.shape[:2]))
        t1 = time.time()

        y, u, v = rgb_to_yuv(image=original_image)
        t2 = time.time()

        u_subs, v_subs = subsample_u_v(u, v, *subsampling_settings)
        t3 = time.time()

        split_y = split(y, block_size)
        split_u = split(u_subs, block_size)
        split_v = split(v_subs, block_size)
        t4 = time.time()

        trans_y = block_dct2(np.array(split_y) - 128, block_size)
        trans_u = block_dct2(np.array(split_u) - 128, block_size)
        trans_v = block_dct2(np.array(split_v) - 128, block_size)
        t5 = time.time()

        quantization_table = quantization_tables[quantization_table_quality]
        quantized_y = quantize(trans_y, quantization_table)
        quantized_u = quantize(trans_u, quantization_table)
        quantized_v = quantize(trans_v, quantization_table)
        t6 = time.time()

        rl_encoded_y = resort_and_run_length_encode(quantized_y, block_size)
        rl_encoded_u = resort_and_run_length_encode(quantized_u, block_size)
        rl_encoded_v = resort_and_run_length_encode(quantized_v, block_size)
        t7 = time.time()

        huffman_code_y = generate_huffman_code(rl_encoded_y)
        huffman_code_u = generate_huffman_code(rl_encoded_u)
        huffman_code_v = generate_huffman_code(rl_encoded_v)
        huff_encoded_y = encode_huffman(huffman_code_y, rl_encoded_y)
        huff_encoded_u = encode_huffman(huffman_code_u, rl_encoded_u)
        huff_encoded_v = encode_huffman(huffman_code_v, rl_encoded_v)
        t8 = time.time()

        compressed_byte_data = image_data_to_bytes(huffman_code_y, huffman_code_u, huffman_code_v,
                                                   huff_encoded_y, huff_encoded_u, huff_encoded_v,
                                                   quantization_table,
                                                   *subsampling_settings,
                                                   *original_image_resolution
                                                   )
        t9 = time.time()

        times_detail = {
            "s0_get_resolution": t1 - t0,
            "s1_split_yuv": t2 - t1,
            "s2_subsample": t3 - t2,
            "s3_split_blocks": t4 - t3,
            "s4_dct": t5 - t4,
            "s5_quantization": t6 - t5,
            "s6_zigzag_rl_encode": t7 - t6,
            "s7_huffman": t8 - t7,
            "s8_binary_conversion": t9 - t8
        }

        return compressed_byte_data, t9 - t0, times_detail

    @staticmethod
    def __decompress(image_data_bytes):
        t0 = time.time()
        code_y, code_u, code_v, encoded_y, encoded_u, encoded_v, quantization_table, j, a, b, x_dim, y_dim = bytes_to_image_data(
            image_data_bytes)

        t1 = time.time()
        rl_encoded_y = decode_huffman(encoded_y, code_y)
        rl_encoded_u = decode_huffman(encoded_u, code_u)
        rl_encoded_v = decode_huffman(encoded_v, code_v)

        t2 = time.time()
        block_size = 8
        y_blocks = unsort_and_run_length_decode(rl_encoded_y, block_size)
        u_blocks = unsort_and_run_length_decode(rl_encoded_u, block_size)
        v_blocks = unsort_and_run_length_decode(rl_encoded_v, block_size)

        t3 = time.time()
        iq_y = quantize_inverse(y_blocks, quantization_table)
        iq_u = quantize_inverse(u_blocks, quantization_table)
        iq_v = quantize_inverse(v_blocks, quantization_table)

        t4 = time.time()
        id_y = block_idct2(iq_y, block_size) + 128
        id_u = block_idct2(iq_u, block_size) + 128
        id_v = block_idct2(iq_v, block_size) + 128

        t5 = time.time()
        subsampling_settings = (j, a, b)
        original_image_resolution = (x_dim, y_dim)
        downsampled_resolution = calculate_down_sampled_resolution(*subsampling_settings, original_image_resolution)

        t6 = time.time()
        compressed_y = merge_blocks(id_y, original_image_resolution, block_size)
        compressed_u = merge_blocks(id_u, downsampled_resolution, block_size)
        compressed_v = merge_blocks(id_v, downsampled_resolution, block_size)
        t7 = time.time()

        compressed_u, compressed_v = up_sample_u_v(compressed_u, compressed_v, *subsampling_settings,
                                                   original_image_resolution)
        t8 = time.time()

        reconstructed_image = yuv_to_rgb(compressed_y, compressed_u, compressed_v)
        reconstructed_image = reconstructed_image.astype(int)
        reconstructed_image = reconstructed_image.clip(0, 255)
        t9 = time.time()

        times_detail = {
            "s0_binary_conversion": t1 - t0,
            "s1_decode_huffman": t2 - t1,
            "s2_inverse_zig_zag_rl": t3 - t2,
            "s3_inverse_quantize": t4 - t3,
            "s4_dct": t5 - t4,
            "s5_reverse_parameters": t6 - t5,
            "s6_merge_blocks": t7 - t6,
            "s7_upsample": t8 - t7,
            "s8_yuv_to_rgb": t9 - t8
        }
        return reconstructed_image, t9 - t0, times_detail

    def show_original(self, title=None):
        fig, ax = plt.subplots()
        ax.imshow(self.original_image)
        if title:
            ax.set_title(title)
        plt.show()

    def get_original(self):
        return self.original_image

    def set_original_file_name(self, name):
        self.original_file_name = name

    def get_decompressed(self):
        return self.decompressed_image

    def get_compression_ratio(self):
        return self.compression_ratio

    def set_compression_ratio(self, ratio):
        self.compression_ratio = ratio

    def show_decompressed(self, title=None):
        fig, ax = plt.subplots()
        ax.imshow(self.get_decompressed().astype(np.uint8))
        if title:
            ax.set_title(title)
        plt.show()

    def get_difference(self, extrapolate=False):
        original_image_rescaled = self.original_image * 255
        original_image_rescaled = original_image_rescaled.astype(int)
        diff = np.abs(original_image_rescaled - self.decompressed_image)

        if extrapolate:
            diff = diff * (255 / np.max(diff))
            diff = diff.astype(int)

        return diff

    def store_compressed(self, path):
        with open(path, "wb") as fp:
            fp.write(self.compressed_byte_data)

    def show_difference(self, title=None, extrapolate=False):
        fig, ax = plt.subplots()
        ax.imshow(self.get_difference(extrapolate))
        if title:
            ax.set_title(title)
        plt.show()

    def store_compressed_png(self, path):
        plt.imsave(path, self.decompressed_image.astype(np.uint8))

    def get_compression_time(self):
        return self.compression_time

    def get_compression_time_details(self):
        return self.compression_time_details

    def get_decompression_time(self):
        return self.decompression_time

    def get_decompression_time_details(self):
        return self.decompression_time_details

    def set_compression_time(self, t):
        self.compression_time = t

    def set_decompression_time(self, t):
        self.decompression_time = t

    def get_peak_signal_to_noise_ratio(self):
        # https://www.geeksforgeeks.org/python-peak-signal-to-noise-ratio-psnr/
        # also correct for rgb (as diff and mean works with multidimensional arrays)
        if np.max(self.original_image) <= 1:
            mse = np.mean(((self.original_image * 255) - self.decompressed_image) ** 2)
        else:
            mse = np.mean((self.original_image - self.decompressed_image) ** 2)

        if mse == 0:
            return np.inf

        psnr = 10 * np.log10((255 ** 2) / mse)
        return psnr

    def get_psnr(self):
        return self.get_peak_signal_to_noise_ratio()

    def show_comparison(self, image_name=None, quality="", subsampling=""):
        fig, ax = plt.subplots(1, 3, figsize=(15, 5.5))

        ax[0].imshow(self.original_image)
        ax[0].set_title("Original Image")
        ax[1].imshow(self.decompressed_image)
        ax[1].set_title("Compressed Image")
        ax[2].imshow(self.get_difference())
        ax[2].set_title("Difference between Original & Compressed")

        file_name = self.original_file_name.split("/")[-1].split(".")[0]  # extract input image path
        description = file_name
        if image_name:
            description = " ".join([image_name, quality, subsampling])

        title = f"{description} Compression ratio: {np.round(self.get_compression_ratio(), 3)}, " \
                f"PSNR: {np.round(self.get_psnr(), 3)}db, " \
                f"Compression time: {np.round(self.get_compression_time(), 4)}s, " \
                f"Decompression time: {np.round(self.get_decompression_time(), 4)}s"

        plt.suptitle(title, fontsize=15)
        plt.tight_layout()
        plt.show()

    def store_comparison(self, out_filename=None, image_name=None, quality="", subsampling=""):
        fig, ax = plt.subplots(1, 3, figsize=(15, 5.5))

        ax[0].imshow(self.original_image)
        ax[0].set_title("Original Image")
        ax[1].imshow(self.decompressed_image)
        ax[1].set_title("Compressed Image")
        ax[2].imshow(self.get_difference())
        ax[2].set_title("Difference between Original & Compressed")

        file_name = self.original_file_name.split("/")[-1].split(".")[0]  # extract input image path
        description = file_name
        if image_name:
            description = " ".join([image_name, quality, subsampling])

        title = f"{description} Compression ratio: {np.round(self.get_compression_ratio(), 3)}, " \
                f"PSNR: {np.round(self.get_psnr(), 3)}db, " \
                f"Compression time: {np.round(self.get_compression_time(), 4)}s, " \
                f"Decompression time: {np.round(self.get_decompression_time(), 4)}s"

        plt.suptitle(title, fontsize=15)
        plt.tight_layout()
        if out_filename:
            plt.savefig(out_filename, dpi=300)
        else:
            plt.savefig(f"results/{file_name}_comparison.png", dpi=300)
        plt.close(fig)


def main():
    image_path = "images/lenna_32x32.png"
    # image_path = "../images/lenna_256x256.png"
    # image_path = "../images/lenna_512x512.png"
    # image_path = "../images/christmas_tree_6000x4000.png"
    # image_path = "../images/Barns_grand_tetons_1600x1195.png"

    # jpeg = EasyJpeg.from_png(image_path, 10, (4, 4, 4), 8)
    #
    # jpeg.show_decompressed()
    # print(jpeg.get_compression_ratio())
    # # jpeg.show_difference()
    # # jpeg.show_difference(extrapolate=True)
    # jpeg.store_compressed("test.out")
    #
    # jpeg2 = EasyJpeg.from_compressed("test.out")
    # # jpeg2.show_decompressed()
    # jpeg2.store_compressed_png("d.png")

    jpeg = EasyJpeg.from_png(image_path, 100, (4, 4, 4), 8)
    # jpeg = EasyJpeg.from_png(image_path, 10, (4, 1, 0), 8)
    print(jpeg.get_compression_time(), jpeg.get_decompression_time())
    # print(jpeg.get_compression_time_details())
    # print(jpeg.get_decompression_time_details())
    print("compression", {k: v for k, v in
                          sorted(jpeg.get_compression_time_details().items(), key=lambda item: item[1], reverse=True)})
    print("decompression", {k: v for k, v in
                            sorted(jpeg.get_decompression_time_details().items(), key=lambda item: item[1],
                                   reverse=True)})
    # t = "results/lenna_64x64_10_(4, 2, 2)_comparison.png"
    # jpeg.store_comparison(t)
    print("psnr", jpeg.get_psnr())
    jpeg.show_comparison()


if __name__ == "__main__":
    main()
