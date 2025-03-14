import pypandoc

def convert_presentation(input_file, output_format='html', output_file=None, extra_args=None):
    if output_file is None:
        output_file = f"presentation.{output_format}"

    # Преобразование файла
    pypandoc.convert_file(
        input_file,
        output_format,
        outputfile=output_file,
        extra_args=extra_args if extra_args else []
    )

    print(f"Презентация успешно сохранена в файл: {output_file}")
    return output_file