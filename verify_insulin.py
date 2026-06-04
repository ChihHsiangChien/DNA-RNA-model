# Human preproinsulin wild-type sequence (UniProt P01308)
WILD_TYPE = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN"

# Standard Genetic Code
GENETIC_CODE = {
    'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
    'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
    'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
    'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
    'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
    'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
    'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
    'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
    'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
    'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
}

# The CORRECTED user sequence segments
block_1 = "ATG GCT CTG TGG ATG CGT CTG CTG CCC CTG CTG GCT CTG CTG GCT CTG TGG GGT CCG GAC CCG GCT GCT GCA"
block_2 = "TTC GTT AAC CAG CAC CTG TGC GGT TCT CAC CTG GTT GAA GCT CTG TAT CTG GTT TGT GGT GAA CGT GGT TTC TTC TAC ACT CCG AAA ACT"
block_3 = "CGT CGT GAA GCT GAA GAC CTG CAG GTT GGT CAG GTT GAA CTG GGT GGT GGT CCG GGT GCT GGT TCT CTG CAG CCG CTG GCT CTG GAA GGT TCT CTG CAG AAA CGT"
block_4 = "GGT ATC GTT GAA CAG TGC TGT ACT TCT ATC TGC TCT CTG TAT CAG CTG GAA AAC TAT TGC AAT TAA"

# Write to text file
with open("insulin_sequence.txt", "w") as f:
    f.write(f"# Signal peptide (24 aa)\n{block_1}\n\n")
    f.write(f"# B chain (Corrected: 30 aa)\n{block_2}\n\n")
    f.write(f"# C-peptide & cleavage sites (Corrected: C-peptide 31 aa + 3 cleavage aa)\n{block_3}\n\n")
    f.write(f"# A chain (21 aa)\n{block_4}\n")

print("Saved corrected sequence to insulin_sequence.txt.")

# Parse and translate
def translate(sequence_str):
    cleaned = "".join([c for c in sequence_str if c.isalpha()]).upper()
    codons = [cleaned[i:i+3] for i in range(0, len(cleaned), 3)]
    protein = []
    for codon in codons:
        if len(codon) < 3:
            continue
        aa = GENETIC_CODE.get(codon, '?')
        if aa == '_':  # Stop codon
            break
        protein.append(aa)
    return "".join(protein), codons

p1, c1 = translate(block_1)
p2, c2 = translate(block_2)
p3, c3 = translate(block_3)
p4, c4 = translate(block_4)

print("\n--- Translation Results (Corrected) ---")
print(f"Block 1 (Signal, expected 24aa): {p1} ({len(p1)} aa)")
print(f"Block 2 (B chain, expected 30aa): {p2} ({len(p2)} aa)")
print(f"Block 3 (C-peptide + cleavage sites, expected 34aa): {p3} ({len(p3)} aa)")
print(f"Block 4 (A chain, expected 21aa): {p4} ({len(p4)} aa)")

translated_total = p1 + p2 + p3 + p4
print(f"\nTotal translated protein: {translated_total} ({len(translated_total)} aa)")
print(f"Wild-type preproinsulin:  {WILD_TYPE} ({len(WILD_TYPE)} aa)")

# Check matching
if translated_total == WILD_TYPE:
    print("\nMATCH: The corrected sequence produces the correct wild-type human preproinsulin!")
else:
    print("\nMISMATCH: The sequence does NOT produce the correct wild-type human preproinsulin.")
