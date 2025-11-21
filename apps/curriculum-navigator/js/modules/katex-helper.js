/**
 * KaTeX Helper - Renders mathematical notation in HTML elements
 * Detects inline ($...$) and display ($$...$$) math expressions
 */

const KatexRenderer = (() => {
  /**
   * Renders LaTeX math expressions in a single element
   * @param {HTMLElement} element - Element containing math text
   */
  function renderInElement(element) {
    if (!element || !window.katex) {
      console.warn('KaTeX library not loaded or element is null');
      return;
    }

    let content = element.innerHTML;

    // Replace display math ($$...$$)
    content = content.replace(/\$\$([^$]+)\$\$/g, (match, math) => {
      try {
        return katex.renderToString(math.trim(), {
          displayMode: true,
          throwOnError: false,
        });
      } catch (e) {
        console.error('KaTeX display math error:', e);
        return match;
      }
    });

    // Replace inline math ($...$)
    content = content.replace(/\$([^$]+)\$/g, (match, math) => {
      try {
        return katex.renderToString(math.trim(), {
          displayMode: false,
          throwOnError: false,
        });
      } catch (e) {
        console.error('KaTeX inline math error:', e);
        return match;
      }
    });

    element.innerHTML = content;
  }

  /**
   * Renders LaTeX in multiple elements
   * @param {NodeList|Array} elements - Collection of elements
   */
  function renderInElements(elements) {
    if (!elements) return;

    Array.from(elements).forEach((el) => renderInElement(el));
  }

  /**
   * Auto-renders math in elements with specific class
   * @param {string} className - Class name to search for (default: 'math-text')
   */
  function autoRender(className = 'math-text') {
    const elements = document.querySelectorAll(`.${className}`);
    renderInElements(elements);
  }

  return {
    renderInElement,
    renderInElements,
    autoRender,
  };
})();

// Make it available globally
if (typeof window !== 'undefined') {
  window.KatexRenderer = KatexRenderer;
}
