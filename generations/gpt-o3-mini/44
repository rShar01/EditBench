import os
import ffmpeg

def compress_video(input_path, output_path, quality='medium'):
    try:
        # Сжимаем видео с учетом выбранного качества и ускорения процесса
        quality_settings = {
            'high': {'crf': 18, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'veryfast'},
            'low': {'crf': 28, 'preset': 'ultrafast'}
        }
        settings = quality_settings.get(quality.lower(), quality_settings['medium'])
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vcodec='libx264', crf=settings['crf'], preset=settings['preset'])
            .run(overwrite_output=True)
        )
        print(f"Сжатие завершено: {output_path} с качеством '{quality}'")
    except ffmpeg.Error as e:
        print(f"Ошибка при сжатии {input_path}: {e}")
        
def compress_videos_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Проходим по всем файлам в входной папке
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        # Проверяем, является ли файл видео
        if os.path.isfile(input_path) and filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            output_path = os.path.join(output_folder, filename)
            # Можно изменить параметр качества на 'high', 'medium' или 'low'
            compress_video(input_path, output_path, quality='medium')

if __name__ == "__main__":
    # Пример использования
    input_folder = r'.\From'  # Укажите путь к вашей входной папке
    output_folder = r'.\To'  # Укажите путь к вашей выходной папке

    compress_videos_in_folder(input_folder, output_folder)
