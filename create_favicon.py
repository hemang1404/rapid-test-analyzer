from PIL import Image, ImageDraw
import os

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)

# Create a simple medical-themed favicon
def create_favicon():
    # Create 32x32 base image
    img = Image.new('RGBA', (32, 32), (16, 185, 129, 255))  # Medical green background
    draw = ImageDraw.Draw(img)
    
    # Draw white medical cross
    # Vertical bar
    draw.rectangle([14, 8, 17, 23], fill=(255, 255, 255, 255))
    # Horizontal bar  
    draw.rectangle([8, 14, 23, 17], fill=(255, 255, 255, 255))
    
    # Save different sizes
    # 32x32 PNG
    img.save('static/favicon-32x32.png', 'PNG')
    
    # 16x16 PNG
    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    img_16.save('static/favicon-16x16.png', 'PNG')
    
    # 180x180 for Apple touch icon
    img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_180.save('static/apple-touch-icon.png', 'PNG')
    
    # ICO file (using 32x32)
    img.save('static/favicon.ico', 'ICO')
    
    print("Favicon files created successfully!")

if __name__ == "__main__":
    create_favicon()
