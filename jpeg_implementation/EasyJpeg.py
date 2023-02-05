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
    compression_ratio = None
    compressed_byte_data = None
    decompressed = None

    def __init__(self, path, quantization_table_quality, subsampling_settings, block_size):
        self.path = path
        self.original_image = plt.imread(self.path)
        # strip alpha channel if exists
        if self.original_image.shape[2] == 4:
            channels = np.dsplit(self.original_image, 4)
            self.original_image = np.dstack(channels[:3])

        self.original_image_resolution = tuple(reversed(self.original_image.shape[:2]))
        self.original_size = os.path.getsize(self.path)
        self.__compress(quantization_table_quality, subsampling_settings, block_size)
        self.__decompress(self.compressed_byte_data)

    def __compress(self, quantization_table_quality, subsampling_settings, block_size):
        if self.compression_ratio:
            return self.compression_ratio

        y, u, v = rgb_to_yuv(image=self.original_image)
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

        self.compressed_byte_data = image_data_to_bytes(huffman_code_y, huffman_code_u, huffman_code_v,
                                                        huff_encoded_y, huff_encoded_u, huff_encoded_v,
                                                        quantization_table
                                                        )
        self.compression_ratio = self.original_size / len(self.compressed_byte_data)

        return self.compression_ratio

    def __decompress(self, image_data_bytes):
        code_y, code_u, code_v, encoded_y, encoded_u, encoded_v, quantization_table = bytes_to_image_data(
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

        subsampling_settings = (4, 4, 0)  # todo save to file
        original_image_resolution = (32, 32)  # todo save to file
        downsampled_resolution = calculate_down_sampled_resolution(*subsampling_settings, original_image_resolution)
        compressed_y = merge_blocks(id_y, original_image_resolution, block_size)
        compressed_u = merge_blocks(id_u, downsampled_resolution, block_size)
        compressed_v = merge_blocks(id_v, downsampled_resolution, block_size)

        compressed_u, compressed_v = up_sample_u_v(compressed_u, compressed_v, *subsampling_settings,
                                                   original_image_resolution)

        reconstructed_image = yuv_to_rgb(compressed_y, compressed_u, compressed_v)
        reconstructed_image = reconstructed_image.astype(int)
        self.decompressed = reconstructed_image.clip(0, 255)

    def show_original(self):
        fig, ax = plt.subplots()
        ax.imshow(self.original_image)
        plt.show()

    def get_original(self):
        return self.original_image

    def get_decompressed(self):
        return self.decompressed

    def show_compressed(self):
        fig, ax = plt.subplots()
        ax.imshow(self.get_decompressed().astype(np.uint8))
        plt.show()

    def get_difference(self, extrapolate=False):
        print(np.max(self.original_image))
        print(np.max(self.decompressed))

        original_image_rescaled = self.original_image * 255
        original_image_rescaled = original_image_rescaled.astype(int)
        diff = np.abs(original_image_rescaled - self.decompressed)

        if extrapolate:
            diff = diff * (255 / np.max(diff))
            diff = diff.astype(int)

        return diff

    def show_difference(self, extrapolate=False):
        fig, ax = plt.subplots()
        ax.imshow(self.get_difference(extrapolate))
        plt.show()


def main():
    image_path = "../images/lenna_32x32.png"

    jpeg = EasyJpeg(image_path, 10, (4, 4, 4), 8)

    jpeg.get_decompressed()
    jpeg.show_difference()
    jpeg.show_difference(extrapolate=True)


if __name__ == "__main__":
    main()
