import os.path

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
    original_image = None
    decompressed_image = None

    compressed_byte_data = None
    compression_ratio = None

    def __init__(self, original_image, decompressed_image, compressed_byte_data, compression_ratio):
        self.original_image = original_image
        self.decompressed_image = decompressed_image
        self.compressed_byte_data = compressed_byte_data
        self.compression_ratio = compression_ratio

    @staticmethod
    def from_png(path, quantization_table_quality, subsampling_settings, block_size):
        original_image = plt.imread(path)
        # strip alpha channel if exists
        if original_image.shape[2] == 4:
            channels = np.dsplit(original_image, 4)
            original_image = np.dstack(channels[:3])

        original_size = os.path.getsize(path)

        compressed_byte_data = EasyJpeg.__compress(original_image, quantization_table_quality, subsampling_settings,
                                                   block_size)
        decompressed_image = EasyJpeg.__decompress(compressed_byte_data)
        compression_ratio = original_size / len(compressed_byte_data)

        return EasyJpeg(original_image, decompressed_image, compressed_byte_data, compression_ratio)

    @staticmethod
    def from_compressed(path):
        with open(path, "rb") as fp:
            data = fp.read()
            decompressed_image = EasyJpeg.__decompress(data)
            return EasyJpeg(None, decompressed_image, data, None)

    @staticmethod
    def __compress(original_image, quantization_table_quality, subsampling_settings, block_size):
        original_image_resolution = tuple(reversed(original_image.shape[:2]))
        y, u, v = rgb_to_yuv(image=original_image)
        u_subs, v_subs = subsample_u_v(u, v, *subsampling_settings)
        split_y = split(y, block_size)
        split_u = split(u_subs, block_size)
        split_v = split(v_subs, block_size)
        trans_y = block_dct2(np.array(split_y) - 128, block_size)
        trans_u = block_dct2(np.array(split_u) - 128, block_size)
        trans_v = block_dct2(np.array(split_v) - 128, block_size)
        quantization_table = quantization_tables[quantization_table_quality]

        quantized_y = quantize(trans_y, quantization_table)
        quantized_u = quantize(trans_u, quantization_table)
        quantized_v = quantize(trans_v, quantization_table)

        rl_encoded_y = resort_and_run_length_encode(quantized_y, block_size)
        rl_encoded_u = resort_and_run_length_encode(quantized_u, block_size)
        rl_encoded_v = resort_and_run_length_encode(quantized_v, block_size)

        huffman_code_y = generate_huffman_code(rl_encoded_y)
        huffman_code_u = generate_huffman_code(rl_encoded_u)
        huffman_code_v = generate_huffman_code(rl_encoded_v)
        huff_encoded_y = encode_huffman(huffman_code_y, rl_encoded_y)
        huff_encoded_u = encode_huffman(huffman_code_u, rl_encoded_u)
        huff_encoded_v = encode_huffman(huffman_code_v, rl_encoded_v)

        compressed_byte_data = image_data_to_bytes(huffman_code_y, huffman_code_u, huffman_code_v,
                                                   huff_encoded_y, huff_encoded_u, huff_encoded_v,
                                                   quantization_table,
                                                   *subsampling_settings,
                                                   *original_image_resolution
                                                   )
        return compressed_byte_data

    @staticmethod
    def __decompress(image_data_bytes):
        code_y, code_u, code_v, encoded_y, encoded_u, encoded_v, quantization_table, j, a, b, x_dim, y_dim = bytes_to_image_data(
            image_data_bytes)
        rl_encoded_y = decode_huffman(encoded_y, code_y)
        rl_encoded_u = decode_huffman(encoded_u, code_u)
        rl_encoded_v = decode_huffman(encoded_v, code_v)

        block_size = 8
        y_blocks = unsort_and_run_length_decode(rl_encoded_y, block_size)
        u_blocks = unsort_and_run_length_decode(rl_encoded_u, block_size)
        v_blocks = unsort_and_run_length_decode(rl_encoded_v, block_size)

        iq_y = quantize_inverse(y_blocks, quantization_table)
        iq_u = quantize_inverse(u_blocks, quantization_table)
        iq_v = quantize_inverse(v_blocks, quantization_table)

        id_y = block_idct2(iq_y, block_size) + 128
        id_u = block_idct2(iq_u, block_size) + 128
        id_v = block_idct2(iq_v, block_size) + 128

        subsampling_settings = (j, a, b)
        original_image_resolution = (x_dim, y_dim)
        downsampled_resolution = calculate_down_sampled_resolution(*subsampling_settings, original_image_resolution)
        compressed_y = merge_blocks(id_y, original_image_resolution, block_size)
        compressed_u = merge_blocks(id_u, downsampled_resolution, block_size)
        compressed_v = merge_blocks(id_v, downsampled_resolution, block_size)

        compressed_u, compressed_v = up_sample_u_v(compressed_u, compressed_v, *subsampling_settings,
                                                   original_image_resolution)

        reconstructed_image = yuv_to_rgb(compressed_y, compressed_u, compressed_v)
        reconstructed_image = reconstructed_image.astype(int)
        return reconstructed_image.clip(0, 255)

    def show_original(self):
        fig, ax = plt.subplots()
        ax.imshow(self.original_image)
        plt.show()

    def get_original(self):
        return self.original_image

    def get_decompressed(self):
        return self.decompressed_image

    def get_compression_ratio(self):
        return self.compression_ratio

    def show_decompressed(self):
        fig, ax = plt.subplots()
        ax.imshow(self.get_decompressed().astype(np.uint8))
        plt.show()

    def get_difference(self, extrapolate=False):
        print(np.max(self.original_image))
        print(np.max(self.decompressed_image))

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

    def show_difference(self, extrapolate=False):
        fig, ax = plt.subplots()
        ax.imshow(self.get_difference(extrapolate))
        plt.show()

    def store_compressed_png(self, path):
        plt.imsave(path, self.decompressed_image.astype(np.uint8))

def main():
    image_path = "../images/lenna_32x32.png"

    jpeg = EasyJpeg.from_png(image_path, 10, (4, 4, 4), 8)

    jpeg.show_decompressed()
    print(jpeg.get_compression_ratio())
    # jpeg.show_difference()
    # jpeg.show_difference(extrapolate=True)
    jpeg.store_compressed("test.out")

    jpeg2 = EasyJpeg.from_compressed("test.out")
    # jpeg2.show_decompressed()
    jpeg2.store_compressed_png("d.png")


if __name__ == "__main__":
    main()
