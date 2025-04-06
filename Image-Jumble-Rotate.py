from PIL import Image


def make_square(input_path, output_path):
    try:
        # Open the original image
        with Image.open(input_path) as img:
            # Get original dimensions
            width, height = img.size
            
            # Determine the size of the square (use the larger dimension)
            new_size = max(width, height)
            
            # Create a new square image with white background
            square_img = Image.new('RGB', (new_size, new_size), (255, 255, 255))
            
            # Calculate position to paste the original image (center it)
            paste_x = (new_size - width) // 2
            paste_y = (new_size - height) // 2
            
            # Paste the original image onto the white square
            square_img.paste(img, (paste_x, paste_y))
            
            # Save the result as JPEG
            square_img.save(output_path, 'JPEG')
            print(f"Successfully converted {input_path} to square image at {output_path}")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
def rotate_quadrants_recursive(input_path, output_path, n):
    """
    Recursively divide image into quadrants and rotate each n times.
    n: number of recursive iterations
    """
    def process_image(img, iterations):
        if iterations <= 0:
            return img
            
        # Get dimensions
        width, height = img.size
        
        # Base case: if image too small to divide, just rotate once
        if width < 2 or height < 2:
            return img.rotate(-90, expand=False)
            
        # Calculate quadrant size
        quad_size_x = width // 2
        quad_size_y = height // 2
        
        # Create new image for this level
        result_img = Image.new('RGB', (width, height))
        
        # Define quadrant coordinates
        quadrants = [
            (0, 0, quad_size_x, quad_size_y),                  # Top-left
            (quad_size_x, 0, width, quad_size_y),             # Top-right
            (0, quad_size_y, quad_size_x, height),            # Bottom-left
            (quad_size_x, quad_size_y, width, height)         # Bottom-right
        ]
        
        # Process each quadrant recursively
        for left, top, right, bottom in quadrants:
            # Crop quadrant
            quad = img.crop((left, top, right, bottom))
            
            # Recursively process this quadrant
            rotated_quad = process_image(quad, iterations - 1)
            
            # Rotate this level's quadrant
            rotated_quad = rotated_quad.rotate(-90, expand=False)
            
            # Paste back in original position
            result_img.paste(rotated_quad, (left, top))
        
        return result_img

    try:
        # Open the original image
        with Image.open(input_path) as img:
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Verify image is square
            width, height = img.size
            if width != height:
                raise ValueError("Input image must be square")
            
            # Process the image recursively
            result = process_image(img, n)
            
            # Save the result
            result.save(output_path, 'JPEG', quality=95)
            print(f"Successfully processed {input_path} with {n} iterations and saved to {output_path}")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def rotate_quadrants_self_center(input_path, output_path):
    try:
        # Open the original image
        with Image.open(input_path) as img:
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get dimensions
            width, height = img.size
            
            # Verify image is square
            if width != height:
                raise ValueError("Input image must be square")
            
            # Calculate quadrant size
            quad_size = width // 2
            
            # Create new image for output
            result_img = Image.new('RGB', (width, height))
            
            # Define quadrant coordinates
            quadrants = [
                (0, 0, quad_size, quad_size),                  # Top-left
                (quad_size, 0, width, quad_size),             # Top-right
                (0, quad_size, quad_size, height),            # Bottom-left
                (quad_size, quad_size, width, height)         # Bottom-right
            ]
            
            # Process each quadrant
            for left, top, right, bottom in quadrants:
                # Crop quadrant
                quad = img.crop((left, top, right, bottom))
                
                # Rotate 90 degrees clockwise around its own center
                rotated_quad = quad.rotate(-90, expand=False)
                
                # Paste back in original position
                result_img.paste(rotated_quad, (left, top))
            
            # Save the result
            result_img.save(output_path, 'JPEG', quality=95)
            print(f"Successfully processed {input_path} and saved to {output_path}")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

 
def reverse_rotate_quadrants_recursive(input_path, output_path, n):
    """
    Reverse the recursive quadrant rotation by rotating counterclockwise n times.
    n: number of recursive iterations to reverse
    """
    def process_image(img, iterations):
        if iterations <= 0:
            return img
            
        # Get dimensions
        width, height = img.size
        
        # Base case: if image too small to divide, just rotate once counterclockwise
        if width < 2 or height < 2:
            return img.rotate(90, expand=False)
            
        # Calculate quadrant size
        quad_size_x = width // 2
        quad_size_y = height // 2
        
        # Create new image for this level
        result_img = Image.new('RGB', (width, height))
        
        # Define quadrant coordinates
        quadrants = [
            (0, 0, quad_size_x, quad_size_y),                  # Top-left
            (quad_size_x, 0, width, quad_size_y),             # Top-right
            (0, quad_size_y, quad_size_x, height),            # Bottom-left
            (quad_size_x, quad_size_y, width, height)         # Bottom-right
        ]
        
        # Process each quadrant recursively
        for left, top, right, bottom in quadrants:
            # Crop quadrant
            quad = img.crop((left, top, right, bottom))
            
            # Rotate this level's quadrant counterclockwise (opposite of original)
            rotated_quad = quad.rotate(90, expand=False)
            
            # Recursively process this quadrant
            processed_quad = process_image(rotated_quad, iterations - 1)
            
            # Paste back in original position
            result_img.paste(processed_quad, (left, top))
        
        return result_img

    try:
        # Open the original image
        with Image.open(input_path) as img:
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Verify image is square
            width, height = img.size
            if width != height:
                raise ValueError("Input image must be square")
            
            # Process the image recursively
            result = process_image(img, n)
            
            # Save the result
            result.save(output_path, 'JPEG', quality=95)
            print(f"Successfully reversed {input_path} with {n} iterations and saved to {output_path}")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Specify your input JPEG and output BMP file paths
    input_file = r"C:\Users\Shiva.Sunar\Downloads\input.jpg"    # Replace with your JPEG file path
    square_jpeg = r"C:\Users\Shiva.Sunar\Downloads\square.jpeg"  # Replace with desired output path
    rotated_jpeg = r"C:\Users\Shiva.Sunar\Downloads\rotated_quadrants.jpeg"  # Replace with desired output path
    undone_jpeg = r"C:\Users\Shiva.Sunar\Downloads\undone_quadrants.jpeg"  # Replace with desired output path
    iteration =5

    make_square(input_file, square_jpeg)
    rotate_quadrants_recursive(square_jpeg, rotated_jpeg, iteration) # Replace with desired output path
    reverse_rotate_quadrants_recursive(rotated_jpeg, undone_jpeg, iteration) # Replace with desired output path
