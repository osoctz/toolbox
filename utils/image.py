from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2


def enhance_image_quality(image_path):
    pass

# 940 * 653
# 952 * 662
def resize_image(image):
    width, height = image.size
    max_len = 952
    # max_len = 1344
    aspect_ratio = width / height

    if width > height:
        new_width = max_len
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = max_len
        new_width = int(new_height * aspect_ratio)

    r_image = image.resize((new_width, new_height), Image.LANCZOS)
    return r_image


def scale_image(image):
    """
    调整亮度和对比度
    :return:
    """
    # 调整亮度
    # enhancer = ImageEnhance.Brightness(image)
    # brightened_image = enhancer.enhance(0.9)  # 1.0表示原始亮度，大于1增加亮度，小于1降低亮度
    # 调整对比度
    enhancer = ImageEnhance.Contrast(image)
    contrasted_image = enhancer.enhance(1.5)  # 1.0表示原始对比度，大于1增加对比度，小于1降低对比度
    # 显示结果
    # contrasted_image.show()
    # 保存结果
    # contrasted_image.save('adjusted_image.jpg')
    return contrasted_image


def sharpened_image(image):
    """
    锐化图片
    :param image:
    :return:
    """
    sh_image = image.convert('L')  # 转换为灰度图像
    # 应用锐化滤镜
    bw_image = sh_image.filter(ImageFilter.SHARPEN)

    # # 保存结果
    # sharpened_image.save('sharpened_image.jpg')
    return bw_image


def equalize_histogram(image):
    """
    直方图均衡化
    :param image:
    :return:
    """
    # image = Image.open(image_path).convert("RGB")
    # 将PIL图像转换为NumPy数组
    img_array = np.array(image.convert("RGB"))

    # 对每个颜色通道分别应用直方图均衡化
    for channel in range(img_array.shape[2]):
        img_array[:, :, channel] = cv2.equalizeHist(img_array[:, :, channel])

    # 将NumPy数组转换回PIL图像
    return Image.fromarray(img_array)


def denoised_image(image_path, output_path):
    # 读取图片
    image = cv2.imread(image_path)
    # 非局部均值去噪
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    # 显示结果
    # cv2.imshow('Denoised Image', denoised_image)
    # cv2.waitKey(0)  # 等待按键关闭窗口
    # cv2.destroyAllWindows()
    # 保存结果
    cv2.imwrite(output_path, denoised_image)


if __name__ == '__main__':
    image = Image.open('/xxx/Downloads/泰语1.png')

    # image=scale_image(image)
    # image=sharpened_image(image)
    # 提高分辨率
    image = resize_image(image)
    image.save('resize_image.png')

    # 调整亮度和对比度
    # scale_image=scale_image(image)
    # scale_image.save('scale_image.png')

    # 锐化
    # sh = sharpened_image(image)
    # sh.save('sh_image.png')

    # 直方图均衡化
    # equalized_image = equalize_histogram(image)
    # equalized_image.save('equalized_image.jpg')

    # 降噪
    # denoised_image('sh_image.jpeg','denoised_image.jpeg')
