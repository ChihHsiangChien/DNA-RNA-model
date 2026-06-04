"""
DNA-RNA Model PDF Generator
This script loads nucleotide PNG images (DNA-A/C/G/T and RNA-A/C/G/U) and generates A4-sized PDFs.
It supports:
1. Scenario 1: Generating full sheets (10x2 grid) of A, T, C, G, or U (both DNA and RNA versions).
2. Scenario 2: Generating double-stranded pairing sheets for a given DNA/RNA sequence.
   - Left column: Coding strand sequence (5' to 3'), with small base indices printed in the left margin.
   - Right column: Complementary strand (3' to 5'), rotated 180 degrees.
   - Footer: Page numbers.
3. Scenario 3: Generating single-stranded layout.
   - Left column: Bases 1-10, with base indices printed in the left margin.
   - Right column: Bases 11-20, with base indices printed in the right margin.
   - Both columns are in normal orientation (not rotated).
   - Footer: Page numbers.
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

# Standard A4 size at 300 DPI for high-quality printing
DPI = 300
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
MM_TO_INCH = 25.4

PAGE_WIDTH = int((A4_WIDTH_MM / MM_TO_INCH) * DPI)  # ~2480 px
PAGE_HEIGHT = int((A4_HEIGHT_MM / MM_TO_INCH) * DPI)  # ~3508 px

# Grid configuration
COLS = 2
ROWS = 10
CELLS_PER_PAGE = COLS * ROWS

# DNA/RNA complementary bases mapping
COMPLEMENT_MAP_DNA = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
COMPLEMENT_MAP_RNA = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}

def load_nucleotide_images(base_dir="."):
    """
    Loads DNA-A/C/G/T and RNA-A/C/G/U from the specified directory.
    Returns a dictionary of loaded PIL Image objects in RGBA mode with keys:
    'DNA-A', 'DNA-C', 'DNA-G', 'DNA-T', 'RNA-A', 'RNA-C', 'RNA-G', 'RNA-U'
    """
    assets = {}
    
    # DNA assets
    for char in ['A', 'C', 'G', 'T']:
        filename = f"DNA-{char}.png"
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            try:
                assets[f"DNA-{char}"] = Image.open(path).convert("RGBA")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Warning: DNA image '{filename}' not found.")
            
    # RNA assets
    for char in ['A', 'C', 'G', 'U']:
        filename = f"RNA-{char}.png"
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            try:
                assets[f"RNA-{char}"] = Image.open(path).convert("RGBA")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Warning: RNA image '{filename}' not found.")
            
    # Fallback to older non-prefix filenames if new ones are completely missing
    for char in ['A', 'C', 'G', 'T', 'U']:
        old_filename = f"{char}.png"
        old_path = os.path.join(base_dir, old_filename)
        if os.path.exists(old_path) and f"DNA-{char}" not in assets and f"RNA-{char}" not in assets:
            try:
                img = Image.open(old_path).convert("RGBA")
                if char in ['A', 'C', 'G', 'T']:
                    assets[f"DNA-{char}"] = img
                if char in ['A', 'C', 'G', 'U']:
                    assets[f"RNA-{char}"] = img
                print(f"Loaded fallback for {char} using legacy {old_filename}")
            except Exception:
                pass
                
    if not assets:
        print("Error: No nucleotide images could be loaded. Please check your filenames.")
        sys.exit(1)
        
    return assets

def get_system_font(size=40):
    """
    Loads a true type font. Tries Arial and Calibri, then falls back to default.
    """
    font_paths = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def calculate_cell_dimensions(page_width, page_height, img_width, img_height, rows=10, cols=2, margin_y=150):
    """
    Calculates the optimum dimensions of cells to fit the A4 page while preserving aspect ratio.
    Ensures that the columns meet exactly in the middle.
    """
    available_height = page_height - 2 * margin_y
    cell_height = int(available_height / rows)
    
    aspect_ratio = img_width / img_height
    cell_width = int(cell_height * aspect_ratio)
    
    # Check if 2 columns fit on the page. If not, scale down.
    total_grid_width = cols * cell_width
    if total_grid_width > page_width:
        cell_width = int(page_width / cols)
        cell_height = int(cell_width / aspect_ratio)
        
    grid_w = cols * cell_width
    grid_h = rows * cell_height
    
    # Calculate starting offsets to center the grid
    start_x = (page_width - grid_w) // 2
    start_y = (page_height - grid_h) // 2
    
    return cell_width, cell_height, start_x, start_y

def create_a4_page(nucleotides_left, nucleotides_right, img_assets, draw_borders=True, rotate_right=True, 
                   page_num=None, total_pages=None, left_indices=None, right_indices=None):
    """
    Creates a single PIL Image representing an A4 page.
    Pastes left nucleotides in column 1 (normal) and right nucleotides in column 2.
    If rotate_right is True, right nucleotides are rotated 180 degrees.
    If page_num is provided, page number text is drawn at the bottom center.
    If left_indices or right_indices are provided, prints small index numbers next to the nucleotides.
    """
    # Create white canvas
    canvas = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(canvas)
    
    # Determine scale size from the first loaded asset
    sample_img = next(iter(img_assets.values()))
    cell_w, cell_h, start_x, start_y = calculate_cell_dimensions(
        PAGE_WIDTH, PAGE_HEIGHT, sample_img.width, sample_img.height, ROWS, COLS, margin_y=150
    )
    
    # Pre-resize and rotate the required assets for performance
    resized_left = {k: v.resize((cell_w, cell_h), Image.Resampling.LANCZOS) for k, v in img_assets.items()}
    if rotate_right:
        resized_right = {k: v.transpose(Image.ROTATE_180).resize((cell_w, cell_h), Image.Resampling.LANCZOS) for k, v in img_assets.items()}
    else:
        resized_right = {k: v.resize((cell_w, cell_h), Image.Resampling.LANCZOS) for k, v in img_assets.items()}
    
    num_rows = max(len(nucleotides_left), len(nucleotides_right))
    
    # Draw borders (cutting lines) for the active rows
    if draw_borders:
        border_color = (200, 200, 200)  # Light gray
        line_width = 3
        
        for i in range(num_rows):
            # Left cell coordinates
            x0_l = start_x
            y0_l = start_y + i * cell_h
            x1_l = start_x + cell_w
            y1_l = y0_l + cell_h
            
            # Right cell coordinates
            x0_r = start_x + cell_w
            y0_r = y0_l
            x1_r = start_x + 2 * cell_w
            y1_r = y1_l
            
            # Draw rectangles around the cells
            draw.rectangle([x0_l, y0_l, x1_l, y1_l], outline=border_color, width=line_width)
            draw.rectangle([x0_r, y0_r, x1_r, y1_r], outline=border_color, width=line_width)
            
    # Paste images
    for i in range(num_rows):
        y_pos = start_y + i * cell_h
        
        # Left column (normal orientation)
        if i < len(nucleotides_left):
            char_l = nucleotides_left[i]
            if char_l in resized_left:
                img_l = resized_left[char_l]
                x_pos_l = start_x
                canvas.paste(img_l, (x_pos_l, y_pos), img_l)
                
        # Right column
        if i < len(nucleotides_right):
            char_r = nucleotides_right[i]
            if char_r in resized_right:
                img_r = resized_right[char_r]
                x_pos_r = start_x + cell_w
                canvas.paste(img_r, (x_pos_r, y_pos), img_r)
                
    # Draw index numbers next to nucleotides if provided
    small_font = get_system_font(size=28)
    
    # Left column numbering (placed in the left margin)
    if left_indices is not None:
        for i, idx in enumerate(left_indices):
            if i >= num_rows:
                break
            text = str(idx)
            try:
                bbox = draw.textbbox((0, 0), text, font=small_font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except Exception:
                text_w, text_h = draw.textsize(text, font=small_font)
            
            # Place to the left of the left cell
            x_pos = start_x - text_w - 20
            y_pos = start_y + i * cell_h + (cell_h - text_h) // 2
            draw.text((x_pos, y_pos), text, font=small_font, fill=(100, 100, 100))
            
    # Right column numbering (placed in the right margin to avoid overlap)
    if right_indices is not None:
        for i, idx in enumerate(right_indices):
            if i >= num_rows:
                break
            text = str(idx)
            try:
                bbox = draw.textbbox((0, 0), text, font=small_font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except Exception:
                text_w, text_h = draw.textsize(text, font=small_font)
                
            # Place to the right of the right cell
            x_pos = start_x + 2 * cell_w + 20
            y_pos = start_y + i * cell_h + (cell_h - text_h) // 2
            draw.text((x_pos, y_pos), text, font=small_font, fill=(100, 100, 100))
            
    # Draw page number at the bottom center if page_num is provided
    if page_num is not None:
        font = get_system_font(size=40)
        if total_pages is not None:
            text = f"Page {page_num} / {total_pages}"
        else:
            text = f"Page {page_num}"
            
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception:
            text_w, text_h = draw.textsize(text, font=font)
            
        x_pos = (PAGE_WIDTH - text_w) // 2
        y_pos = PAGE_HEIGHT - 80
        draw.text((x_pos, y_pos), text, font=font, fill=(100, 100, 100))
        
    return canvas

def generate_scenario_1(img_assets, draw_borders=True):
    """
    Scenario 1: Generate sheets where the whole page is filled with a single nucleotide.
    Generates DNA and RNA sheets separately.
    """
    dna_nucleotides = ['A', 'T', 'C', 'G']
    rna_nucleotides = ['A', 'U', 'C', 'G']
    
    generated_files = []
    
    print("\n--- Generating Scenario 1 (Full Sheets) ---")
    
    # 1. DNA Sheets
    dna_pages = []
    for char in dna_nucleotides:
        key = f"DNA-{char}"
        if key not in img_assets:
            continue
        left_seq = [key] * ROWS
        right_seq = [key] * ROWS
        
        page_img = create_a4_page(left_seq, right_seq, img_assets, draw_borders, rotate_right=True, page_num=1, total_pages=1)
        out_filename = f"sheet_DNA-{char}.pdf"
        page_img.save(out_filename, "PDF")
        print(f"Generated: {out_filename}")
        generated_files.append(out_filename)
        dna_pages.append(page_img)
        
    if dna_pages:
        # Save combined DNA version
        combined_dna_filename = "sheet_DNA_all.pdf"
        # Re-save with page numbers
        pages_combined = []
        for i, char in enumerate(dna_nucleotides):
            key = f"DNA-{char}"
            left_seq = [key] * ROWS
            right_seq = [key] * ROWS
            p_img = create_a4_page(left_seq, right_seq, img_assets, draw_borders, rotate_right=True, page_num=i+1, total_pages=len(dna_nucleotides))
            pages_combined.append(p_img)
        pages_combined[0].save(combined_dna_filename, save_all=True, append_images=pages_combined[1:])
        print(f"Generated combined DNA document: {combined_dna_filename}")
        generated_files.append(combined_dna_filename)
        
    # 2. RNA Sheets
    rna_pages = []
    for char in rna_nucleotides:
        key = f"RNA-{char}"
        if key not in img_assets:
            continue
        left_seq = [key] * ROWS
        right_seq = [key] * ROWS
        
        page_img = create_a4_page(left_seq, right_seq, img_assets, draw_borders, rotate_right=True, page_num=1, total_pages=1)
        out_filename = f"sheet_RNA-{char}.pdf"
        page_img.save(out_filename, "PDF")
        print(f"Generated: {out_filename}")
        generated_files.append(out_filename)
        rna_pages.append(page_img)
        
    if rna_pages:
        # Save combined RNA version
        combined_rna_filename = "sheet_RNA_all.pdf"
        pages_combined = []
        for i, char in enumerate(rna_nucleotides):
            key = f"RNA-{char}"
            left_seq = [key] * ROWS
            right_seq = [key] * ROWS
            p_img = create_a4_page(left_seq, right_seq, img_assets, draw_borders, rotate_right=True, page_num=i+1, total_pages=len(rna_nucleotides))
            pages_combined.append(p_img)
        pages_combined[0].save(combined_rna_filename, save_all=True, append_images=pages_combined[1:])
        print(f"Generated combined RNA document: {combined_rna_filename}")
        generated_files.append(combined_rna_filename)
        
    return generated_files

def generate_scenario_2(sequence, img_assets, draw_borders=True, output_filename="dna_sequence_paired.pdf"):
    """
    Scenario 2: Given a DNA/RNA sequence, generate double-stranded pairing sheets.
    Left column contains the coding sequence (5' to 3'), right column contains the complement.
    Small base numbering indices are printed next to the coding strand (left column).
    """
    # Clean sequence (remove all whitespaces)
    sequence = "".join(sequence.split()).upper()
    if not sequence:
        print("Error: Empty sequence provided.")
        return []
        
    # Detect DNA vs RNA
    is_rna = 'U' in sequence
    comp_map = COMPLEMENT_MAP_RNA if is_rna else COMPLEMENT_MAP_DNA
    prefix = "RNA-" if is_rna else "DNA-"
    
    # Validate characters
    valid_bases = set(comp_map.keys())
    invalid_chars = [c for c in sequence if c not in valid_bases]
    if invalid_chars:
        print(f"Warning: Found invalid base characters {set(invalid_chars)}. They will be ignored.")
        sequence = "".join([c for c in sequence if c in valid_bases])
        
    if not sequence:
        print("Error: No valid bases remain in the sequence.")
        return []
        
    # Generate left and complementary right sequences with correct prefixes
    left_seq = [f"{prefix}{base}" for base in sequence]
    right_seq = [f"{prefix}{comp_map[base]}" for base in sequence]
    
    # Paginate (10 rows per page)
    pages = []
    total_len = len(left_seq)
    total_pages = (total_len + ROWS - 1) // ROWS
    
    print(f"\n--- Generating Scenario 2 ({'RNA' if is_rna else 'DNA'} Paired Sequence: {sequence}) ---")
    print(f"Total bases: {total_len} | Total pages: {total_pages}")
    
    for page_idx in range(total_pages):
        start = page_idx * ROWS
        end = min(start + ROWS, total_len)
        
        p_left = left_seq[start:end]
        p_right = right_seq[start:end]
        
        # Coding strand (left column) index numbers
        left_indices = list(range(start + 1, end + 1))
        
        # Create page (right column rotated 180 degrees)
        page_img = create_a4_page(
            p_left, p_right, img_assets, 
            draw_borders=draw_borders, 
            rotate_right=True, 
            page_num=page_idx + 1, 
            total_pages=total_pages,
            left_indices=left_indices,
            right_indices=None  # Only number the coding strand
        )
        pages.append(page_img)
        
    if pages:
        pages[0].save(output_filename, save_all=True, append_images=pages[1:])
        print(f"Generated: {output_filename}")
        return [output_filename]
        
    return []

def generate_scenario_3(sequence, img_assets, draw_borders=True, output_filename="single_strand_sequence.pdf"):
    """
    Scenario 3: Given a single-stranded sequence, generate sequential single strand pages.
    Left column contains bases 1-10, right column contains bases 11-20. Then page changes.
    Right column is in normal orientation (no rotation).
    Small base numbering indices are printed next to both columns.
    """
    # Clean sequence (remove all whitespaces)
    sequence = "".join(sequence.split()).upper()
    if not sequence:
        print("Error: Empty sequence provided.")
        return []
        
    # Detect DNA vs RNA
    is_rna = 'U' in sequence
    comp_map = COMPLEMENT_MAP_RNA if is_rna else COMPLEMENT_MAP_DNA
    prefix = "RNA-" if is_rna else "DNA-"
    
    # Validate characters
    valid_bases = set(comp_map.keys())
    invalid_chars = [c for c in sequence if c not in valid_bases]
    if invalid_chars:
        print(f"Warning: Found invalid base characters {set(invalid_chars)}. They will be ignored.")
        sequence = "".join([c for c in sequence if c in valid_bases])
        
    if not sequence:
        print("Error: No valid bases remain in the sequence.")
        return []
        
    # Convert sequence bases into asset keys
    full_seq = [f"{prefix}{base}" for base in sequence]
    
    # Each page contains up to 20 bases (10 left, 10 right)
    bases_per_page = ROWS * COLS  # 20
    total_len = len(full_seq)
    total_pages = (total_len + bases_per_page - 1) // bases_per_page
    
    print(f"\n--- Generating Scenario 3 ({'RNA' if is_rna else 'DNA'} Single Strand Sequence: {sequence}) ---")
    print(f"Total bases: {total_len} | Total pages: {total_pages}")
    
    pages = []
    for page_idx in range(total_pages):
        page_start = page_idx * bases_per_page
        
        # Left column (first 10 bases on this page)
        left_start = page_start
        left_end = min(left_start + ROWS, total_len)
        p_left = full_seq[left_start:left_end]
        left_indices = list(range(left_start + 1, left_end + 1))
        
        # Right column (next 10 bases on this page)
        right_start = page_start + ROWS
        right_end = min(right_start + ROWS, total_len)
        
        if right_start < total_len:
            p_right = full_seq[right_start:right_end]
            right_indices = list(range(right_start + 1, right_end + 1))
        else:
            p_right = []
            right_indices = None
        
        # Create page (right column is NOT rotated)
        page_img = create_a4_page(
            p_left, p_right, img_assets, 
            draw_borders=draw_borders, 
            rotate_right=False, 
            page_num=page_idx + 1, 
            total_pages=total_pages,
            left_indices=left_indices,
            right_indices=right_indices
        )
        pages.append(page_img)
        
    if pages:
        pages[0].save(output_filename, save_all=True, append_images=pages[1:])
        print(f"Generated: {output_filename}")
        return [output_filename]
        
    return []

def read_multiline_sequence(prompt, default_file=None):
    print(prompt)
    if default_file and os.path.exists(default_file):
        print(f"(Press Enter to use default sequence file: {default_file},")
        print(" or copy-paste multiple lines and press Enter twice to finish, or enter another filename):")
    else:
        print("(You can copy-paste multiple lines. Press Enter twice to finish, or enter a filename):")
    
    lines = []
    while True:
        try:
            line = input().strip()
            if not line:
                if len(lines) == 0 and default_file and os.path.exists(default_file):
                    line = default_file
                else:
                    break
            
            # If the very first line entered is a filename and exists, read it
            if len(lines) == 0 and os.path.exists(line):
                try:
                    with open(line, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Clean content (remove lines starting with #, and keep only letters)
                    clean_lines = []
                    for file_line in content.splitlines():
                        file_line = file_line.strip()
                        if not file_line or file_line.startswith('#'):
                            continue
                        clean_lines.append(file_line)
                    print(f"Loaded sequence from file: {line}")
                    return "".join(clean_lines)
                except Exception as e:
                    print(f"Error reading file {line}: {e}")
                    continue
            lines.append(line)
        except EOFError:
            break
    return "".join(lines)

def main():
    parser = argparse.ArgumentParser(description="DNA-RNA Nucleotide A4 PDF Generator")
    parser.add_argument("--mode", choices=["1", "2", "3", "5", "all", "combo", "interactive"], default="interactive",
                        help="Mode: 1=Scenario 1 (Full sheets), 2=Scenario 2 (Paired), 3=Scenario 3 (Single Strand), 5=Combo (DNA ds, DNA ss, mRNA ss), all=Run all, interactive=Interactive menu")
    parser.add_argument("--seq", type=str, default="", help="DNA/RNA sequence for Scenarios 2 & 3 (e.g. ATCGATCG)")
    parser.add_argument("--no-borders", action="store_true", help="Disable cell borders/cutting lines")
    parser.add_argument("--output", type=str, default="", help="Custom output filename")
    
    args = parser.parse_args()
    
    # Load assets
    img_assets = load_nucleotide_images()
    draw_borders = not args.no_borders
    mode = args.mode
    
    if mode == "interactive":
        print("=" * 55)
        print("        DNA-RNA Nucleotide PDF Layout Generator")
        print("=" * 55)
        print("1. Scenario 1: Generate full A4 sheets for each base (DNA-A/T/C/G & RNA-A/U/C/G)")
        print("2. Scenario 2: Generate double-stranded pairing A4 sheets (rotated complement)")
        print("3. Scenario 3: Generate single-stranded sequential A4 sheets (left -> right col)")
        print("4. Generate All Scenarios (Scenario 1, 2, 3)")
        print("5. Generate DNA ds, DNA ss, & mRNA ss from a DNA sequence (Combo)")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice == "1":
            mode = "1"
        elif choice == "2":
            mode = "2"
        elif choice == "3":
            mode = "3"
        elif choice == "4" or choice == "all":
            mode = "all"
        elif choice == "5" or choice == "combo":
            mode = "combo"
        elif choice == "6":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Exiting...")
            sys.exit(0)
            
    # Resolve sequence if Scenario 2, Scenario 3, All, or Combo are run
    seq = ""
    if mode in ["2", "3", "all", "combo"]:
        seq = args.seq
        if not seq:
            # Determine prompt based on mode
            if mode == "all":
                prompt = "\nEnter DNA/RNA Sequence for Scenarios 2 & 3:"
            elif mode == "combo":
                prompt = "\nEnter DNA Sequence (e.g. ATCGATCG) to generate DNA ds, DNA ss & mRNA ss:"
            elif mode == "2":
                prompt = "\nEnter DNA/RNA Sequence for Scenario 2 (e.g. ATCGATCG):"
            else:
                prompt = "\nEnter DNA/RNA Sequence for Scenario 3 (e.g. ATCGATCG):"
            
            # Choose the default file intelligently based on mode
            if mode == "3":
                if os.path.exists("insulin_mrna_sequence.txt"):
                    default_file = "insulin_mrna_sequence.txt"
                else:
                    default_file = "insulin_sequence.txt" if os.path.exists("insulin_sequence.txt") else None
            else:
                default_file = "insulin_sequence.txt" if os.path.exists("insulin_sequence.txt") else None
                
            seq = read_multiline_sequence(prompt, default_file)
            
    if mode == "1" or mode == "all":
        generate_scenario_1(img_assets, draw_borders)
        
    if mode == "2" or mode == "all":
        output_file = args.output if args.output else "dna_sequence_paired.pdf"
        generate_scenario_2(seq, img_assets, draw_borders, output_file)
        
    if mode == "3" or mode == "all":
        output_file = args.output if args.output else "single_strand_sequence.pdf"
        generate_scenario_3(seq, img_assets, draw_borders, output_file)

    if mode == "combo":
        # Generate DNA ds (double-stranded pairing)
        dna_paired = args.output if args.output else "dna_sequence_paired.pdf"
        print("\n=== Generating 1/3: DNA Double-Stranded (Paired) ===")
        generate_scenario_2(seq, img_assets, draw_borders, dna_paired)

        # Generate DNA ss (single-stranded sequential)
        dna_single = "dna_sequence_single.pdf"
        print("\n=== Generating 2/3: DNA Single-Stranded ===")
        generate_scenario_3(seq, img_assets, draw_borders, dna_single)

        # Generate mRNA ss (single-stranded sequential, replacing T with U)
        mrna_seq = seq.upper().replace('T', 'U')
        mrna_single = "mrna_sequence_single.pdf"
        print("\n=== Generating 3/3: mRNA Single-Stranded ===")
        generate_scenario_3(mrna_seq, img_assets, draw_borders, mrna_single)
        
        print("\n=== Combo Generation Completed! ===")
        print(f"1. DNA Paired (ds): {dna_paired}")
        print(f"2. DNA Single (ss): {dna_single}")
        print(f"3. mRNA Single (ss): {mrna_single}")

if __name__ == "__main__":
    main()
