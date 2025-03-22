from PIL import Image, ImageEnhance, ImageFilter


def resize_and_process(path, pixel_size:int) -> str:
	out_path = f'{path}.processed.png'
	dims = (pixel_size, pixel_size) 

	with Image.open(path) as img:
		img = ImageEnhance.Contrast(img).enhance(2.0)
		img = img.filter(ImageFilter.SHARPEN)

        # Calculate aspect ratio for (pre-crop) resize
		aspect_ratio = img.size[0] / img.size[1]
		if aspect_ratio > 1:
			new_width  = int(dims[1] * aspect_ratio)
			new_height = dims[1]
		else:
			new_width  = dims[0]
			new_height = int(dims[0] / aspect_ratio)

		img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

		# Calculate cropping box (centered)
		left   = (img.width  - dims[0]) / 2
		top    = (img.height - dims[1]) / 2
		right  = (img.width  + dims[0]) / 2
		bottom = (img.height + dims[1]) / 2

		img = img.crop((left, top, right, bottom))
        
		img.save(out_path, format='GIF', optimize=True)
	return out_path


