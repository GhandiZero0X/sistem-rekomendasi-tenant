import os
from PIL import Image

def batch_convert_to_webp(input_folder, output_folder, quality=80):
    """
    Convert & compress semua gambar PNG/JPG/JPEG ke WEBP di folder output.

    Params:
        input_folder (str): Folder berisi file gambar
        output_folder (str): Folder output untuk file WEBP
        quality (int): Kualitas kompresi WEBP (1–100)
    """

    # Ekstensi yang didukung
    valid_ext = (".png", ".jpg", ".jpeg")

    # Pastikan output folder ada
    os.makedirs(output_folder, exist_ok=True)

    # Loop seluruh file di folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_ext):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".webp"
            output_path = os.path.join(output_folder, output_filename)

            with Image.open(input_path) as img:
                img = img.convert("RGB")  # samakan format warna
                img.save(output_path, "WEBP", quality=quality, method=6)

            print(f"Converted: {filename} → {output_filename}")

    print("\nAll images have been successfully converted to WEBP!")


if __name__ == "__main__":
    input_folder = "tenant/"
    output_folder = "tenant_converted/"

    batch_convert_to_webp(input_folder, output_folder, quality=70)
