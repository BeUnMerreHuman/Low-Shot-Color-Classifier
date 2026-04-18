import os
import argparse
import json
import numpy as np
from PIL import Image
import onnxruntime as ort

def rgb_to_hsv_numpy(rgb):
   
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    v = maxc
    
    deltac = maxc - minc
    s = np.divide(deltac, maxc, out=np.zeros_like(maxc), where=maxc != 0)
    
    deltac_nonzero = np.where(deltac == 0, 1, deltac)
    
    rc = (maxc - r) / deltac_nonzero
    gc = (maxc - g) / deltac_nonzero
    bc = (maxc - b) / deltac_nonzero
    
    h = np.zeros_like(maxc)
    h = np.where(r == maxc, bc - gc, h)
    h = np.where(g == maxc, 2.0 + rc - bc, h)
    h = np.where(b == maxc, 4.0 + gc - rc, h)
    
    h = (h / 6.0) % 1.0
    return np.stack([h, s, v], axis=-1)

def load_system_config(model_dir):
    config_path = os.path.join(model_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration not found at {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

def preprocess_image(image_path, img_size, pad_color):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    s = max(w, h)
    padded = Image.new("RGB", (s, s), tuple(pad_color))
    padded.paste(img, ((s - w) // 2, (s - h) // 2))
    
    resized = padded.resize((img_size, img_size), Image.LANCZOS)
    rgb_array = np.array(resized).astype(np.float32) / 255.0
    
    hsv_array = rgb_to_hsv_numpy(rgb_array)
    return hsv_array

def main():
    parser = argparse.ArgumentParser(description="ONNX Inference pipeline for Khilona classification.")
    parser.add_argument("--image", required=True, help="Path to the target image file.")
    parser.add_argument("--model_dir", required=True, help="Directory containing config.json and .onnx model.")
    args = parser.parse_args()

    cfg = load_system_config(args.model_dir)
    img_size = cfg["img_size"]
    pad_color = cfg["pad_color"]
    classes = cfg["classes"]

    model_path = os.path.join(args.model_dir, "khilona_model.onnx")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No ONNX model found at {model_path}")
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    input_array = preprocess_image(args.image, img_size, pad_color)
    
    batch_tensor = np.expand_dims(input_array, axis=0).astype(np.float32)

    outputs = session.run(None, {input_name: batch_tensor})
    predictions = outputs[0][0] 

    predicted_idx = np.argmax(predictions)
    predicted_class = classes[predicted_idx]
    confidence = predictions[predicted_idx]

    print("\n" + "="*40)
    print(" ONNX INFERENCE RESULTS")
    print("="*40)
    print(f" Predicted Class : {predicted_class}")
    print(f" Confidence      : {confidence * 100:.2f}%\n")
    
    print(" Class Probabilities:")
    for cls_name, prob in zip(classes, predictions):
        print(f"  - {cls_name:<8}: {prob * 100:.2f}%")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()