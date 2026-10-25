"""
Generate Parichay Deep Teal + Mint + Warm Ivory Vector Assets
Matching the exact visual language of the reference screenshots:
1. parichay-art.svg (Full split-screen artwork with sage canvas and overlapping gradient lozenges)
2. parichay-mark.svg (Square brand icon emblem)
3. parichay-logo.svg (Horizontal brand lockup with name & tagline)
4. favicon.svg (Favicon)
"""
import os

def generate_brand_assets():
    out_dir = "d:/Parichay/static/images"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Full Split-Screen Hero & Auth Canvas Artwork (480 x 560)
    # Sage canvas with two overlapping isometric rounded gradient lozenges
    art_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 580" width="100%" height="100%" fill="none">
  <defs>
    <!-- Back Lozenge: Deep Teal to Mint Gradient -->
    <linearGradient id="tealMintGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#123B35" />
      <stop offset="40%" stop-color="#2D7A68" />
      <stop offset="80%" stop-color="#6BBF9E" />
      <stop offset="100%" stop-color="#A8F0C6" />
    </linearGradient>

    <!-- Front Lozenge: Warm Peach to Terracotta/Amber Gradient -->
    <linearGradient id="peachAmberGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCE5CE" />
      <stop offset="30%" stop-color="#F9BE8B" />
      <stop offset="70%" stop-color="#F28E58" />
      <stop offset="100%" stop-color="#E26D46" />
    </linearGradient>

    <!-- Soft Ambient Dropshadows -->
    <filter id="lozengeShadow" x="-20%" y="-20%" width="150%" height="150%">
      <feDropShadow dx="0" dy="16" stdDeviation="24" flood-color="#123B35" flood-opacity="0.12" />
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#123B35" flood-opacity="0.08" />
    </filter>

    <filter id="frontShadow" x="-20%" y="-20%" width="150%" height="150%">
      <feDropShadow dx="-6" dy="12" stdDeviation="18" flood-color="#202622" flood-opacity="0.15" />
    </filter>
  </defs>

  <!-- Sage Background Container with soft rounded corners -->
  <rect width="500" height="580" rx="28" fill="#DCEFE3" />

  <!-- Center Group: Two Interlocking / Overlapping Diagonal Lozenges -->
  <g transform="translate(250, 290) rotate(-38)">
    <!-- Back Lozenge: Teal to Mint (Potential & Foundation) -->
    <g transform="translate(-75, -25)" filter="url(#lozengeShadow)">
      <rect x="-105" y="-170" width="210" height="340" rx="95" fill="url(#tealMintGrad)" />
    </g>

    <!-- Front Lozenge: Peach to Terracotta (Opportunity & Growth) with translucent overlap -->
    <g transform="translate(65, 25)" filter="url(#frontShadow)">
      <rect x="-105" y="-170" width="210" height="340" rx="95" fill="url(#peachAmberGrad)" opacity="0.94" />
    </g>
  </g>
</svg>'''

    with open(os.path.join(out_dir, "parichay-art.svg"), "w", encoding="utf-8") as f:
        f.write(art_svg)

    # 2. Square Brand Emblem (64 x 64)
    # Mini version of the two overlapping lozenges
    mark_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" fill="none">
  <defs>
    <linearGradient id="markTealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#123B35" />
      <stop offset="50%" stop-color="#2D7A68" />
      <stop offset="100%" stop-color="#6BBF9E" />
    </linearGradient>
    <linearGradient id="markPeachGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCE5CE" />
      <stop offset="60%" stop-color="#F28E58" />
      <stop offset="100%" stop-color="#E26D46" />
    </linearGradient>
    <filter id="markShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-1" dy="2" stdDeviation="2.5" flood-color="#123B35" flood-opacity="0.18" />
    </filter>
  </defs>

  <g transform="translate(32, 32) rotate(-38) scale(0.12)">
    <!-- Back Lozenge (Teal) -->
    <g transform="translate(-70, -20)">
      <rect x="-105" y="-165" width="210" height="330" rx="90" fill="url(#markTealGrad)" />
    </g>
    <!-- Front Lozenge (Peach) -->
    <g transform="translate(65, 20)" filter="url(#markShadow)">
      <rect x="-105" y="-165" width="210" height="330" rx="90" fill="url(#markPeachGrad)" opacity="0.92" />
    </g>
  </g>
</svg>'''

    with open(os.path.join(out_dir, "parichay-mark.svg"), "w", encoding="utf-8") as f:
        f.write(mark_svg)
    with open(os.path.join(out_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(mark_svg)

    # 3. Horizontal Full Brand Lockup (360 x 54)
    logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 54" width="380" height="54" fill="none">
  <defs>
    <linearGradient id="logoTealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#123B35" />
      <stop offset="50%" stop-color="#2D7A68" />
      <stop offset="100%" stop-color="#6BBF9E" />
    </linearGradient>
    <linearGradient id="logoPeachGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCE5CE" />
      <stop offset="60%" stop-color="#F28E58" />
      <stop offset="100%" stop-color="#E26D46" />
    </linearGradient>
    <filter id="logoShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-1" dy="2" stdDeviation="2" flood-color="#123B35" flood-opacity="0.16" />
    </filter>
  </defs>

  <!-- Left Icon Emblem -->
  <g transform="translate(26, 27) rotate(-38) scale(0.105)">
    <g transform="translate(-70, -20)">
      <rect x="-105" y="-165" width="210" height="330" rx="90" fill="url(#logoTealGrad)" />
    </g>
    <g transform="translate(65, 20)" filter="url(#logoShadow)">
      <rect x="-105" y="-165" width="210" height="330" rx="90" fill="url(#logoPeachGrad)" opacity="0.94" />
    </g>
  </g>

  <!-- Brand Typography -->
  <g transform="translate(58, 0)">
    <text x="0" y="27" font-family="'Plus Jakarta Sans', sans-serif" font-size="24" font-weight="800" letter-spacing="-0.03em" fill="#123B35">Parichay</text>
    <text x="1" y="44" font-family="'Inter', sans-serif" font-size="11" font-weight="500" letter-spacing="-0.01em" fill="#6F7872">Where Your Potential Meets Opportunity.</text>
  </g>
</svg>'''

    with open(os.path.join(out_dir, "parichay-logo.svg"), "w", encoding="utf-8") as f:
        f.write(logo_svg)

    print("All Parichay Deep Teal & Mint brand assets generated successfully!")

if __name__ == '__main__':
    generate_brand_assets()
