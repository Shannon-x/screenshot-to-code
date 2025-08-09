"""
Enhanced Prompts System - Layered Architecture for Better Code Generation
"""

# Base Layer - Common rules for all frameworks
BASE_GENERATION_RULES = """
CRITICAL RULES FOR HIGH-QUALITY CODE GENERATION:

1. ACCURACY AND PRECISION:
   - Match the screenshot EXACTLY in terms of layout, colors, spacing, and content
   - Use precise color values (extract exact hex/rgb from screenshot)
   - Match font sizes, weights, and families precisely
   - Preserve exact spacing, padding, and margins
   - Never omit elements - if there are 20 items in the screenshot, generate 20 items

2. MODERN WEB STANDARDS:
   - Use semantic HTML5 elements (header, nav, main, section, article, footer)
   - Implement proper accessibility (alt text, ARIA labels, semantic structure)
   - Ensure proper meta tags and viewport settings
   - Use modern CSS features (flexbox, grid, custom properties)

3. CODE QUALITY:
   - Write complete, production-ready code - NO PLACEHOLDERS OR COMMENTS
   - Use consistent indentation and formatting
   - Implement proper error handling for interactive elements
   - Ensure cross-browser compatibility

4. IMAGE HANDLING:
   - For placeholder images, use https://placehold.co with appropriate dimensions
   - Include detailed alt text describing the image content and purpose
   - Use responsive image techniques (srcset, sizes) where appropriate
   - Consider loading="lazy" for images below the fold
"""

# Modern UI Components Layer
MODERN_UI_GUIDELINES = """
MODERN UI IMPLEMENTATION GUIDELINES:

1. VISUAL HIERARCHY AND DEPTH:
   - Use appropriate shadows for elevation:
     * Subtle: shadow-sm for slight elevation
     * Cards: shadow-md for standard cards
     * Modals/Popups: shadow-xl for prominent elements
   - Apply proper border radius:
     * Buttons: rounded-md or rounded-lg
     * Cards: rounded-lg or rounded-xl
     * Images: rounded-lg with overflow-hidden

2. INTERACTIVE STATES:
   - Hover effects: transform scale, shadow changes, color transitions
   - Focus states: visible focus rings for accessibility
   - Active states: slight scale reduction or darker shade
   - Disabled states: reduced opacity and cursor-not-allowed
   - Loading states: skeleton screens or spinners

3. TRANSITIONS AND ANIMATIONS:
   - Add smooth transitions: transition-all duration-200 ease-in-out
   - Hover animations: transform hover:scale-105
   - Color transitions: transition-colors duration-150
   - Use transform for performance over position changes

4. MODERN COMPONENTS:
   - Cards with proper spacing and shadows
   - Modals with backdrop blur
   - Tooltips with proper positioning
   - Dropdown menus with smooth animations
   - Toggle switches instead of checkboxes where appropriate
   - Skeleton loaders for async content

5. COLOR SCHEMES:
   - Support dark mode with appropriate color variables
   - Use consistent color palette throughout
   - Proper contrast ratios for accessibility (WCAG AA minimum)
   - Subtle gradients for modern look where appropriate
"""

# Responsive Design Layer
RESPONSIVE_DESIGN_RULES = """
RESPONSIVE DESIGN IMPLEMENTATION:

1. MOBILE-FIRST APPROACH:
   - Start with mobile layout (default styles)
   - Progressive enhancement for larger screens
   - Use min-width media queries (sm:, md:, lg:, xl:, 2xl:)

2. BREAKPOINT STRATEGY:
   - Mobile: < 640px (default)
   - Tablet: sm:640px, md:768px
   - Desktop: lg:1024px, xl:1280px
   - Wide: 2xl:1536px

3. RESPONSIVE PATTERNS:
   - Navigation: Mobile hamburger → Desktop horizontal menu
   - Grid layouts: Stack on mobile → Multi-column on desktop
   - Text sizing: Smaller on mobile → Larger on desktop
   - Spacing: Tighter on mobile → More spacious on desktop

4. FLEXIBLE COMPONENTS:
   - Use relative units (rem, em, %) over fixed pixels
   - Flexible images: max-w-full h-auto
   - Container with responsive padding: px-4 sm:px-6 lg:px-8
   - Responsive typography scale

5. LAYOUT STRATEGIES:
   - CSS Grid for complex layouts: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
   - Flexbox for component layouts: flex flex-col md:flex-row
   - Container queries where supported
   - Aspect ratio boxes for media
"""

# Framework-Specific Enhancements
TAILWIND_SPECIFIC_ENHANCEMENTS = """
TAILWIND CSS BEST PRACTICES:

1. UTILITY ORGANIZATION:
   - Layout utilities first (flex, grid, position)
   - Spacing utilities next (p-, m-, gap-)
   - Styling utilities (bg-, text-, border-)
   - State utilities last (hover:, focus:, active:)

2. COMMON PATTERNS:
   - Card: "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
   - Button: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
   - Input: "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"

3. CUSTOM UTILITIES:
   - Use @apply sparingly in style tags for repeated patterns
   - Leverage Tailwind's color palette consistently
   - Use space utilities for consistent spacing
"""

REACT_SPECIFIC_ENHANCEMENTS = """
REACT COMPONENT BEST PRACTICES:

1. COMPONENT STRUCTURE:
   - Use functional components with hooks
   - Implement proper state management with useState/useReducer
   - Use useEffect for side effects
   - Memoize expensive computations with useMemo

2. PERFORMANCE:
   - Use React.memo for pure components
   - Implement lazy loading with React.lazy
   - Use proper key props in lists
   - Avoid inline function definitions in render

3. PATTERNS:
   - Custom hooks for reusable logic
   - Component composition over inheritance
   - Proper prop validation with TypeScript/PropTypes
"""

# Image Processing Guidelines
ENHANCED_IMAGE_GUIDELINES = """
INTELLIGENT IMAGE HANDLING:

1. IMAGE TYPE DETECTION:
   - Logos: Usually in header/footer, use smaller dimensions (150x50)
   - Hero images: Full width, use responsive sizes (1920x1080, 1280x720, 640x360)
   - Product images: Square or portrait, consistent aspect ratios
   - Icons: Small, square dimensions (24x24, 32x32, 48x48)
   - Avatars: Circular, square dimensions (40x40, 64x64, 128x128)

2. PLACEHOLDER STRATEGIES:
   - Primary service: https://placehold.co/{width}x{height}
   - Backup: https://via.placeholder.com/{width}x{height}
   - Include text overlay for clarity: ?text=Hero+Image
   - Use appropriate colors matching the design

3. RESPONSIVE IMAGES:
   - srcset for different resolutions
   - sizes attribute for responsive behavior
   - Picture element for art direction
   - loading="lazy" for performance

4. ALT TEXT QUALITY:
   - Descriptive: "Team of developers collaborating in modern office"
   - Functional: "Click to open product gallery"
   - Informative: "Graph showing 40% increase in user engagement"
"""

def get_enhanced_system_prompt(framework: str, complexity_level: str = "standard", is_imported_code: bool = False, is_text_mode: bool = False) -> str:
    """
    Generate an enhanced system prompt based on framework and complexity level
    
    Args:
        framework: The target framework (html_tailwind, react_tailwind, etc.)
        complexity_level: simple, standard, or complex
        is_imported_code: Whether this is for imported code
        is_text_mode: Whether this is for text-based generation
        
    Returns:
        Enhanced system prompt string
    """
    # Get the appropriate base prompt
    if is_imported_code:
        from prompts.imported_code_prompts import IMPORTED_CODE_SYSTEM_PROMPTS
        base_framework_prompt = IMPORTED_CODE_SYSTEM_PROMPTS.get(framework, "")
    elif is_text_mode:
        from prompts.text_prompts import SYSTEM_PROMPTS as TEXT_SYSTEM_PROMPTS
        base_framework_prompt = TEXT_SYSTEM_PROMPTS.get(framework, "")
    else:
        from prompts.screenshot_system_prompts import SYSTEM_PROMPTS
        base_framework_prompt = SYSTEM_PROMPTS.get(framework, "")
    
    # Combine with enhanced guidelines
    enhanced_prompt = base_framework_prompt + "\n\n" + BASE_GENERATION_RULES + "\n\n" + MODERN_UI_GUIDELINES + "\n\n" + RESPONSIVE_DESIGN_RULES
    
    # Add framework-specific enhancements
    if "tailwind" in framework.lower():
        enhanced_prompt += "\n\n" + TAILWIND_SPECIFIC_ENHANCEMENTS
    
    if "react" in framework.lower():
        enhanced_prompt += "\n\n" + REACT_SPECIFIC_ENHANCEMENTS
    
    # Add image guidelines (only for screenshot mode)
    if not is_text_mode and not is_imported_code:
        enhanced_prompt += "\n\n" + ENHANCED_IMAGE_GUIDELINES
    
    # Adjust based on complexity
    if complexity_level == "complex":
        enhanced_prompt += "\n\nFor this complex interface, pay extra attention to:\n"
        enhanced_prompt += "- Nested component hierarchies\n"
        enhanced_prompt += "- Advanced state management\n"
        enhanced_prompt += "- Multiple interactive elements\n"
        enhanced_prompt += "- Complex grid layouts\n"
    elif complexity_level == "simple":
        enhanced_prompt += "\n\nFor this simple interface, focus on:\n"
        enhanced_prompt += "- Clean, minimal code\n"
        enhanced_prompt += "- Basic interactions\n"
        enhanced_prompt += "- Clear structure\n"
    
    return enhanced_prompt

def get_dynamic_temperature(complexity_level: str, framework: str) -> float:
    """
    Get dynamic temperature based on complexity and framework
    
    Args:
        complexity_level: simple, standard, or complex
        framework: The target framework
        
    Returns:
        Temperature value between 0.0 and 0.3
    """
    base_temp = 0.1
    
    if complexity_level == "complex":
        base_temp += 0.1  # More creativity for complex layouts
    elif complexity_level == "simple":
        base_temp = 0.05  # Less creativity for simple layouts
    
    # Some frameworks benefit from slightly higher temperature
    if framework in ["react_tailwind", "vue_tailwind"]:
        base_temp += 0.05
    
    return min(base_temp, 0.3)  # Cap at 0.3

def get_variant_count(complexity_level: str) -> int:
    """
    Get the number of variants to generate based on complexity
    
    Args:
        complexity_level: simple, standard, or complex
        
    Returns:
        Number of variants (2-6)
    """
    if complexity_level == "complex":
        return 6
    elif complexity_level == "standard":
        return 4
    else:  # simple
        return 2

def analyze_image_complexity(image_data: str) -> str:
    """
    Analyze image to determine complexity level
    This is a placeholder - in real implementation, would use image analysis
    
    Args:
        image_data: Base64 encoded image data
        
    Returns:
        Complexity level: simple, standard, or complex
    """
    # TODO: Implement actual image analysis
    # For now, return standard as default
    return "standard"