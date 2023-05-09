# from pathlib import Path

# from aa_pbs_exporter.pbs_2022_01.parse_pbs_txt import parse_pbs_txt
# from aa_pbs_exporter.snippets.pdf.extract_text_from_pdf_to_file import (
#     extract_text_from_pdf_to_file,
# )


# def parse_pbs_pdf(
#     pdf_file: Path,
#     output_dir: Path,
#     debug: bool = False,
#     rename_txt: bool = True,
# ):
#     output_path = output_dir / pdf_file.name
#     output_path = output_path.with_suffix(".txt")
#     extract_text_from_pdf_to_file(file_in=pdf_file, file_out=output_path)
#     parse_pbs_txt(
#         txt_file=output_path,
#         output_dir=output_dir,
#         debug=debug,
#         include_source=False,
#         rename_source=rename_txt,
#     )
