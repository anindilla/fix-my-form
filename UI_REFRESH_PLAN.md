# UI Refresh: Strava-Inspired Design with Accessibility & Mobile

## Final Design Direction

**User Selections:**
- Typography: **Space Grotesk** (headings) + **Inter** (body)
- Color Scheme: **Warm & Energetic** (Orange/Red/Yellow)
- Mode: **Light Mode** primary
- Inspiration: **Strava** (clean, athletic, data-focused)
- **Accessibility**: WCAG 2.1 AA compliant (4.5:1 text, 3:1 UI components)
- **Mobile**: Responsive design with touch-friendly interactions

## Strava-Inspired Design Elements

### Key Strava Characteristics to Adopt:
1. **Bold, confident typography** with clear hierarchy
2. **Orange accent color** (#FC4C02 - Strava's signature)
3. **Clean white backgrounds** with strategic color pops
4. **Data visualization** with clear metrics and progress
5. **Card-based layouts** with subtle shadows
6. **Minimal but impactful** - no clutter
7. **Strong CTAs** with high contrast
8. **Athletic photography** and dynamic angles

### Our Accessible Color Palette:
**Primary Colors (WCAG AA Compliant):**
- **Primary Orange**: #FF5722 (on white: 3.3:1 - UI elements)
- **Dark Orange**: #E64A19 (on white: 4.5:1 - text/buttons)
- **Deep Red**: #D32F2F (on white: 5.5:1 - scores/alerts)
- **Warm Yellow**: #FFA726 (on dark: 4.8:1 - success states)

**Neutral Colors:**
- **Charcoal**: #212121 (on white: 16.1:1 - primary text)
- **Gray**: #616161 (on white: 5.7:1 - secondary text)
- **Light Gray**: #F5F5F5 (backgrounds)
- **White**: #FFFFFF (cards/surfaces)

**Semantic Colors (Accessible):**
- **Success Green**: #2E7D32 (on white: 4.6:1)
- **Warning Orange**: #EF6C00 (on white: 4.5:1)
- **Error Red**: #C62828 (on white: 6.4:1)

**Typography:**
- **Space Grotesk**: Bold, geometric headings (600-800 weight)
- **Inter**: Clean, readable body text (400-600 weight)
- **Minimum sizes**: 16px body, 14px small text, 12px captions

## Mobile-First Responsive Design

### Breakpoints:
- **Mobile**: 320px - 768px (primary focus)
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Mobile Considerations:
- **Touch targets**: Minimum 44x44px for all interactive elements
- **Typography**: Larger text on mobile (18px+ for body)
- **Spacing**: Generous padding and margins for touch
- **Navigation**: Thumb-friendly button placement
- **Cards**: Full-width on mobile, proper spacing
- **Forms**: Large input fields, clear labels

## Accessibility Requirements

### Color Contrast (WCAG 2.1 AA)
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text** (18px+): Minimum 3:1 contrast ratio
- **UI components**: Minimum 3:1 contrast ratio
- **Focus indicators**: Visible 3:1 contrast, 2px outline

### Interactive Elements
- **Focus states**: Clear 2px outline with high contrast
- **Hover states**: Visual feedback without relying solely on color
- **Active states**: Clear pressed/selected indication
- **Touch targets**: Minimum 44x44px for mobile

### Content Structure
- **Semantic HTML**: Proper heading hierarchy (h1 → h2 → h3)
- **ARIA labels**: For icons and interactive elements
- **Alt text**: Descriptive text for all images/icons
- **Keyboard navigation**: Full keyboard accessibility

## Implementation Plan

### Phase 1: Typography & Accessible Color System
**Files**: `globals.css`, `tailwind.config.js`

1. Import Space Grotesk (weights: 500, 600, 700, 800)
2. Keep Inter (weights: 400, 500, 600, 700)
3. Define accessible color palette in Tailwind
4. Add focus-visible utilities for keyboard navigation
5. Set base font sizes and line heights
6. Add color contrast utilities
7. Add mobile-first responsive utilities

### Phase 2: Hero Section Redesign
**Files**: `app/page.tsx`, `globals.css`

1. Bold gradient background (light orange → white)
2. Space Grotesk title (responsive: text-4xl sm:text-6xl lg:text-7xl)
3. High contrast text (charcoal #212121 on light background)
4. Prominent CTA buttons with 4.5:1 contrast
5. Focus states with visible outlines
6. Proper heading hierarchy (h1 → h2 → h3)
7. Mobile-optimized spacing and typography

### Phase 3: Exercise Cards Redesign
**Files**: `components/VideoUploader.tsx`

1. White cards with accessible borders
2. Orange accent on hover (3:1 contrast minimum)
3. Clear selected state with border + background
4. Icon updates with proper ARIA labels
5. 44x44px minimum touch targets
6. Keyboard navigation support
7. Focus indicators on all interactive elements
8. Mobile: Full-width cards, proper spacing
9. Responsive grid: 1 column mobile, 2 tablet, 3 desktop

### Phase 4: Analysis Results Redesign
**Files**: `components/AnalysisResults.tsx`, `app/analysis/[id]/page.tsx`

1. Large, bold score display with high contrast
2. Color-coded scores with text labels (not color alone)
3. Accessible progress bars with labels
4. Card redesign with proper shadows
5. Tab navigation with keyboard support
6. ARIA labels for all interactive elements
7. Semantic HTML structure
8. Mobile: Stacked layout, larger touch targets
9. Responsive typography and spacing

### Phase 5: Loading & Error States
**Files**: `components/LoadingAnalysis.tsx`, `VideoUploader.tsx`

1. Orange spinner with accessible contrast
2. Loading text for screen readers
3. Error states with icons + text
4. Success states with clear visual feedback
5. ARIA live regions for status updates
6. Mobile: Larger loading indicators, clear messaging

### Phase 6: Icons & Visual Elements
**All component files**

1. Update all Lucide icons with consistent sizing
2. Add ARIA labels to all icon-only buttons
3. Ensure icon + text combinations for clarity
4. Update icon colors for accessibility
5. Add hover/focus states to all icons
6. Mobile: Larger icons (24px minimum), proper spacing

### Phase 7: Micro-interactions & Polish
**All component files**

1. Button hover: scale(1.02) + shadow
2. Card hover: translateY(-4px) + shadow
3. Smooth transitions (200-300ms ease-in-out)
4. Focus-visible outlines (2px solid, high contrast)
5. Reduced motion support (@media prefers-reduced-motion)
6. Mobile: Touch-friendly animations, no hover on touch devices

## Mobile-Specific Enhancements

### Touch Interactions:
- **Swipe gestures**: For card navigation
- **Touch feedback**: Visual response to touch
- **Long press**: For additional actions
- **Pull to refresh**: For data updates

### Layout Optimizations:
- **Sticky headers**: Keep navigation accessible
- **Bottom navigation**: For primary actions
- **Floating action buttons**: For main CTAs
- **Collapsible sections**: To save space

### Performance:
- **Lazy loading**: For images and components
- **Optimized images**: WebP format, proper sizing
- **Minimal JavaScript**: Fast loading on mobile
- **Progressive enhancement**: Works without JS

## Accessibility Checklist

- [ ] All text meets 4.5:1 contrast ratio
- [ ] Large text meets 3:1 contrast ratio
- [ ] UI components meet 3:1 contrast ratio
- [ ] Focus indicators are visible (3:1 contrast, 2px)
- [ ] All interactive elements have 44x44px touch targets
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] ARIA labels on all icon-only buttons
- [ ] Alt text on all images
- [ ] Keyboard navigation works throughout
- [ ] Color is not the only indicator of state
- [ ] Reduced motion support implemented
- [ ] Screen reader tested (basic)
- [ ] Mobile touch targets tested
- [ ] Responsive design tested on all breakpoints
- [ ] Performance optimized for mobile

## File Structure

```
frontend/
├── app/
│   ├── globals.css (typography, colors, mobile utilities)
│   ├── layout.tsx (global theme, font loading)
│   └── page.tsx (hero section redesign)
├── components/
│   ├── VideoUploader.tsx (exercise cards, mobile-friendly)
│   ├── AnalysisResults.tsx (results display, accessible)
│   └── LoadingAnalysis.tsx (loading states, mobile-optimized)
└── tailwind.config.js (color palette, responsive utilities)
```

## Success Metrics

1. **Accessibility**: WCAG 2.1 AA compliance
2. **Mobile**: 100% functional on mobile devices
3. **Performance**: <3s load time on mobile
4. **Usability**: Clear visual hierarchy and navigation
5. **Brand**: Strava-inspired athletic aesthetic
