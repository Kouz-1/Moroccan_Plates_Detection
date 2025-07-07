import json
import string
import os

def save_plate_to_json(pred_file='predictions.txt', json_file='json_plates/plates.json'):
    # Ensure the predictions.txt exists
    if not os.path.exists(pred_file):
        print(f"{pred_file} does not exist.")
        return

    # Step 1: Load predictions
    with open(pred_file, 'r') as f:
        lines = f.readlines()

    # Extract predicted characters only
    chars = [line.strip().split(': ')[1] for line in lines if ': ' in line]

    # Step 2: Find the first alphabetic character (A–Z, or 'WAW', etc.)
    alphabet_set = set(string.ascii_uppercase + 'WAW')  # Add more Arabic letters if needed
    letter_idx = next((i for i, c in enumerate(chars) if c.upper() in alphabet_set), None)

    if letter_idx is None:
        print("No alphabetic character found in predictions. Skipping entry.")
        return

    number = ''.join(chars[:letter_idx])
    char = chars[letter_idx]
    region = ''.join(chars[letter_idx + 1:])

    # Step 3: Prepare JSON entry
    new_entry = {
        "number": number,
        "char": char,
        "region": region
    }

    # Step 4: Append to plates.json
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(new_entry)

    with open(json_file, 'w') as jf:
        json.dump(data, jf, indent=4)

    print(f"✅ Plate saved: {new_entry}")

    # Step 5: Clear predictions.txt
    with open(pred_file, 'w') as f:
        f.write('')
    print("🧹 Cleared predictions.txt.")

if __name__ == "__main__":
    save_plate_to_json()

