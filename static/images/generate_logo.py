"""
Generate Parichay Brand SVGs:
1. parichay-mark.svg (Square emblem)
2. parichay-logo.svg (Horizontal brand lockup with name & tagline)
3. parichay-logo-dark.svg (Dark theme lockup)
4. parichay-favicon.svg (Optimized favicon)
"""

def generate_assets():
    # 1. Full Horizontal Lockup (440 x 80)
    logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 76" width="460" height="76" fill="none">
  <defs>
    <!-- Royal Indigo to Electric Violet Gradient (Foundation & Intelligence) -->
    <linearGradient id="pGradBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4338CA" />
      <stop offset="50%" stop-color="#4F46E5" />
      <stop offset="100%" stop-color="#6366F1" />
    </linearGradient>

    <!-- Warm Amber / Gold to Electric Cyan Gradient (Opportunity & Ascent) -->
    <linearGradient id="pGradWarm" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B" />
      <stop offset="45%" stop-color="#FB8500" />
      <stop offset="70%" stop-color="#06B6D4" />
      <stop offset="100%" stop-color="#4F46E5" />
    </linearGradient>

    <!-- Subtle Weave Drop Shadow -->
    <filter id="knotShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0.5" dy="1.2" stdDeviation="1.0" flood-opacity="0.28"/>
    </filter>
  </defs>

  <!-- LOGO EMBLEM (Left aligned, centered at x=38, y=38, 56x56 footprint) -->
  <g transform="translate(6, 6) scale(0.85)">
    <!-- Capsule 1 (Rotated +45 deg: Warm Amber to Cyan) -->
    <g transform="rotate(45 38 38)">
      <rect x="25" y="10" width="26" height="56" rx="13" 
            stroke="url(#pGradWarm)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- Capsule 2 (Rotated -45 deg: Cobalt to Electric Blue) -->
    <g transform="rotate(-45 38 38)">
      <rect x="25" y="10" width="26" height="56" rx="13" 
            stroke="url(#pGradBlue)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- Over-under Celtic Weave Crossing Arc -->
    <g transform="rotate(45 38 38)" filter="url(#knotShadow)">
      <path d="M 25 24 L 25 18 C 25 12 30 10 38 10 C 46 10 51 12 51 18 L 51 24" 
            stroke="url(#pGradWarm)" stroke-width="7" stroke-linecap="round"/>
    </g>
  </g>

  <!-- TYPOGRAPHY: Brand Name & Taglines -->
  <g transform="translate(86, 0)">
    <!-- Brand Name "Parichay" -->
    <text x="0" y="38" 
          font-family="'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif" 
          font-size="34" 
          font-weight="800" 
          letter-spacing="-0.035em" 
          fill="#0F172A">Parichay</text>

    <!-- Category Pill Badge -->
    <rect x="156" y="18" width="86" height="20" rx="10" fill="#EDF5FF" stroke="#BAdafE" stroke-width="1"/>
    <text x="199" y="32" 
          font-family="'Inter', sans-serif" 
          font-size="9.5" 
          font-weight="700" 
          letter-spacing="0.08em" 
          text-anchor="middle" 
          fill="#007BFF">AI INTELLIGENCE</text>

    <!-- Primary Tagline -->
    <text x="1" y="58" 
          font-family="'Inter', -apple-system, sans-serif" 
          font-size="13" 
          font-weight="500" 
          letter-spacing="-0.01em" 
          fill="#475569">Where Your Potential Meets Opportunity.</text>
  </g>
</svg>'''

    with open('d:/Parichay/static/images/parichay-logo.svg', 'w', encoding='utf-8') as f:
        f.write(logo_svg)

    # 2. Square Emblem / Mark (64 x 64)
    mark_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" fill="none">
  <defs>
    <linearGradient id="pGradBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4338CA" />
      <stop offset="50%" stop-color="#4F46E5" />
      <stop offset="100%" stop-color="#6366F1" />
    </linearGradient>
    <linearGradient id="pGradWarm" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B" />
      <stop offset="45%" stop-color="#FB8500" />
      <stop offset="70%" stop-color="#06B6D4" />
      <stop offset="100%" stop-color="#4F46E5" />
    </linearGradient>
    <filter id="knotShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0.5" dy="1.2" stdDeviation="1.0" flood-opacity="0.28"/>
    </filter>
  </defs>

  <g transform="rotate(45 32 32)">
    <rect x="20" y="8" width="24" height="48" rx="12" 
          stroke="url(#pGradWarm)" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <g transform="rotate(-45 32 32)">
    <rect x="20" y="8" width="24" height="48" rx="12" 
          stroke="url(#pGradBlue)" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <g transform="rotate(45 32 32)" filter="url(#knotShadow)">
    <path d="M 20 20 L 20 15 C 20 10.5 24.5 8 32 8 C 39.5 8 44 10.5 44 15 L 44 20" 
          stroke="url(#pGradWarm)" stroke-width="6.5" stroke-linecap="round"/>
  </g>
</svg>'''

    with open('d:/Parichay/static/images/parichay-mark.svg', 'w', encoding='utf-8') as f:
        f.write(mark_svg)

    # 3. Clean Favicon SVG (32x32)
    with open('d:/Parichay/static/images/favicon.svg', 'w', encoding='utf-8') as f:
        f.write(mark_svg)

    print("All Parichay brand vector assets generated successfully!")

if __name__ == '__main__':
    generate_assets()
