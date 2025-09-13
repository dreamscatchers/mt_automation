
def generate_prompt_by_number(index):
    styles = [
        "Impressionist", "Cubist", "Baroque", "Art Deco", "Art Nouveau",
        "Pop Art", "Engraving", "Watercolor", "Anime", "Watercolor"
    ]

    places = [
        "mountain at sunrise", "sun-dappled forest", "desert landscape",
        "Buddhist temple", "modern city rooftop", "candle-lit cave",
        "cosmic space", "underwater realm", "flowering garden", "abstract spiritual plane"
    ]

    clothes = [
        "traditional Buddhist robe", "white yogic garments", "crimson ceremonial cloak",
        "golden spiritual attire", "modern minimalist outfit", "nothing but radiant energy",
        "mystical armor", "Indian dhoti and sash", "futuristic meditation suit", "transparent light body"
    ]

    template = """
A serene male meditator sits cross-legged in a {place}, rendered in the {style} style. He wears a {clothes}, appropriate for the atmosphere and tradition. His posture is upright and composed, exuding calmness and inner stillness.

His hands are positioned near his chest, each clearly showing five distinct fingers. The index fingers touch at their tips to form a small, upward-pointing triangle. The middle, ring, and pinky fingers curl inward into the palms, while the thumbs rest gently and visibly atop them. The hand gesture is symmetrical, and the anatomy is rendered with realistic human proportions and precise finger placement.

    The figure’s hands are held near the chest in a precise meditative gesture (Maha Gyan Mudra):
    – The index fingers are extended and touch at the tips, forming a small upward-pointing triangle.
    – The left hand is turned inward, palm facing the chest.
    – The right hand is turned outward, palm facing away.
    – The other fingers are curled inward into fists.
    – The right thumb rests gently over the curled fingers, the left thumb is tucked in.
    – Each hand must visibly include four anatomically correct fingers.
    Four fingers should be visible, three bent and the index finger

The surrounding environment supports the contemplative mood — whether through light, color, or texture — reinforcing the meditative focus of the scene. The composition is balanced, drawing the viewer's attention to the hands, face, and overall harmony of body and background.

Above the figure, the title "MASTER'S TOUCH MEDITATION" arches gently, complementing the mood and style of the artwork.
aspect ratio 16:9
""".strip()

    if not (1 <= index <= 1000):
        raise ValueError("Index must be between 1 and 1000")

    index -= 1  # zero-based
    style = styles[index % 10]
    place = places[(index // 10) % 10]
    clothing = clothes[index // 100]

    return template.format(style=style, place=place, clothes=clothing)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python description_generator.py <number from 1 to 1000>")
        sys.exit(1)

    try:
        number = int(sys.argv[1])
        print(generate_prompt_by_number(number))
    except ValueError as e:
        print("Error:", e)
        sys.exit(1)
