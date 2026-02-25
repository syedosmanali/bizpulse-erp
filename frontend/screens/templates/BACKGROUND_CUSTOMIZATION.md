# Background Image Customization Guide

## Overview
The ERP system now features a beautiful 4K nature background that appears behind all module content while keeping the sidebar visible.

## Current Setup
- **Image Source**: Unsplash 4K nature image (forest scene)
- **Position**: Behind main content, in front of sidebar
- **Overlay**: White semi-transparent layer (85% opacity) with 2px blur
- **Responsive**: Adapts to all screen sizes

## How to Replace the Background Image

### Option 1: Use Your Own Local Image

1. Save your image to: `frontend/assets/static/images/background.jpg`
   - Recommended size: 2560x1440 or higher (4K)
   - Supported formats: JPG, PNG, WebP

2. Update the CSS in `erp_base_layout.html`:
   ```css
   .background-layer {
       background-image: url('/static/images/background.jpg');
   }
   ```

### Option 2: Use External URL

Update the CSS in `erp_base_layout.html`:
```css
.background-layer {
    background-image: url('YOUR_IMAGE_URL_HERE');
}
```

## Customization Options

### Adjust Overlay Opacity
Find `.background-layer::before` in the CSS and modify:

- **More visible content** (less visible background):
  ```css
  background: rgba(255, 255, 255, 0.90);
  ```

- **More visible background** (less overlay):
  ```css
  background: rgba(255, 255, 255, 0.75);
  ```

- **Current balanced setting**:
  ```css
  background: rgba(255, 255, 255, 0.85);
  ```

### Adjust Blur Effect
Modify the `backdrop-filter` property:
```css
backdrop-filter: blur(2px);  /* Current: subtle blur */
backdrop-filter: blur(5px);  /* More blur */
backdrop-filter: blur(0px);  /* No blur */
```

### Change Background Position
```css
background-position: center;      /* Current: centered */
background-position: top;         /* Focus on top */
background-position: bottom;      /* Focus on bottom */
background-position: left center; /* Focus on left */
```

### Change Background Size
```css
background-size: cover;   /* Current: fills entire area */
background-size: contain; /* Fits entire image */
background-size: 100% 100%; /* Stretches to fit */
```

## Recommended Images

### Free Stock Photo Sources:
- **Unsplash**: https://unsplash.com/s/photos/nature
- **Pexels**: https://www.pexels.com/search/nature/
- **Pixabay**: https://pixabay.com/images/search/nature/

### Image Guidelines:
- Resolution: 2560x1440 or higher
- Aspect ratio: 16:9 or wider
- Style: Soft, natural colors work best
- Avoid: High contrast or busy patterns
- File size: Keep under 2MB for fast loading

## Technical Details

### CSS Structure:
```css
.background-layer {
    position: fixed;           /* Stays in place on scroll */
    left: var(--sidebar-width); /* Starts after sidebar */
    z-index: -1;               /* Behind content */
    background-attachment: fixed; /* Parallax effect */
}

.background-layer::before {
    /* White overlay for readability */
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(2px);
}
```

### Mobile Responsive:
On mobile devices (< 768px), the background extends to full width:
```css
@media (max-width: 768px) {
    .background-layer {
        left: 0; /* Full width on mobile */
    }
}
```

## Troubleshooting

### Background not showing?
- Check image URL is correct
- Verify image file exists in the specified path
- Check browser console for 404 errors

### Content not readable?
- Increase overlay opacity (higher value = more white)
- Increase blur effect
- Choose a lighter background image

### Performance issues?
- Compress your image (use tools like TinyPNG)
- Use WebP format for better compression
- Reduce image resolution if needed

## Examples

### Dark Overlay (for light backgrounds):
```css
.background-layer::before {
    background: rgba(0, 0, 0, 0.3); /* Dark overlay */
}
```

### Colored Overlay:
```css
.background-layer::before {
    background: rgba(115, 44, 63, 0.85); /* Wine-colored overlay */
}
```

### No Overlay (pure background):
```css
.background-layer::before {
    display: none; /* Remove overlay completely */
}
```

## Support
For additional customization help, refer to the main CSS in `erp_base_layout.html` or consult the development team.
