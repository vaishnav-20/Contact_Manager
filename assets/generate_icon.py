from PIL import Image, ImageDraw
import os

def create_app_icon(output_dir="assets"):
    os.makedirs(output_dir, exist_ok=True)
    size = (256, 256)
    
    # 1. Base Image with transparency
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors: Royal Palette
    navy_dark = (11, 19, 43, 255)       # #0b132b
    navy_light = (28, 37, 65, 255)      # #1c2541
    gold = (212, 175, 55, 255)          # #d4af37
    gold_bright = (243, 198, 35, 255)   # #f3c623
    sapphire = (37, 99, 235, 255)       # #2563eb
    white = (248, 250, 252, 255)        # #f8fafc
    
    # Rounded badge background
    pad = 12
    draw.rounded_rectangle([pad, pad, 256-pad, 256-pad], radius=50, fill=navy_dark, outline=gold, width=6)
    
    # Inner decorative rounded card (address book body)
    book_left, book_top, book_right, book_bottom = 44, 40, 212, 216
    draw.rounded_rectangle([book_left, book_top, book_right, book_bottom], radius=24, fill=navy_light, outline=gold_bright, width=3)
    
    # Spine strip on left
    draw.rounded_rectangle([book_left, book_top, book_left + 32, book_bottom], radius=16, fill=sapphire)
    # Golden binder rings
    for y in [76, 116, 156, 196]:
        draw.ellipse([book_left + 10, y - 6, book_left + 22, y + 6], fill=gold_bright)
        
    # Golden bookmark ribbon hanging from top right
    ribbon_x = 166
    draw.polygon([(ribbon_x, book_top), (ribbon_x + 20, book_top), (ribbon_x + 20, book_top + 38), 
                  (ribbon_x + 10, book_top + 28), (ribbon_x, book_top + 38)], fill=gold_bright)
    
    # Silhouette: Contact head and shoulders in center
    center_x = 136
    head_y = 104
    head_radius = 26
    draw.ellipse([center_x - head_radius, head_y - head_radius, center_x + head_radius, head_y + head_radius], fill=white)
    
    # Shoulders / Torso
    torso_top = 138
    torso_width = 46
    draw.chord([center_x - torso_width, torso_top, center_x + torso_width, torso_top + 52], 
               start=0, end=180, fill=white)
    
    # Star badge at bottom right of contact symbol
    star_x = 180
    star_y = 180
    star_r = 14
    draw.ellipse([star_x - star_r, star_y - star_r, star_x + star_r, star_y + star_r], fill=gold_bright, outline=navy_dark, width=2)
    
    # Save PNG
    png_path = os.path.join(output_dir, "app_icon.png")
    img.save(png_path, format="PNG")
    print(f"Saved PNG to {png_path}")
    
    # Save ICO with multiple sizes
    ico_path = os.path.join(output_dir, "app_icon.ico")
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Saved ICO to {ico_path}")

if __name__ == "__main__":
    create_app_icon()
