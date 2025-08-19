# import requests
# import base64

# def generate_ai_image(prompt, n_images=9):
#     """
#     Generate images using the free Craiyon API for a given prompt.
#     Returns a list of local image filenames.
#     """
#     url = "https://backend.craiyon.com/generate"
#     response = requests.post(url, json={"prompt": prompt})
#     if response.status_code != 200:
#         raise Exception(f"Craiyon API Error: {response.text}")
#     result = response.json()
#     images = result.get("images", [])
#     img_paths = []
#     for i, b64img in enumerate(images):
#         img_path = f"craiyon_{i+1}.png"
#         with open(img_path, "wb") as f:
#             f.write(base64.b64decode(b64img))
#         img_paths.append(img_path)
#         if len(img_paths) >= n_images:
#             break
#     return img_paths
from PIL import Image, ImageDraw, ImageFont

def generate_ai_image(text, out_path="generated.jpg", width=1080, height=1080):
    img = Image.new("RGB", (width, height), "#f8b500")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=72)
    except:
        font = ImageFont.load_default()
    text_width, text_height = draw.textsize(text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, font=font, fill="white")
    img.save(out_path)
    return out_path
