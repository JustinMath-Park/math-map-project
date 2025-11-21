/**
 * KaTeX 렌더링 헬퍼
 */
const KatexRenderer = {
    /**
     * 여러 요소에 KaTeX 렌더링 적용
     * @param {NodeList|Array} elements - 렌더링할 요소들
     */
    renderInElements(elements) {
        elements.forEach(el => {
            try {
                this.renderInElement(el);
            } catch (e) {
                console.warn("KaTeX 렌더링 오류:", e, el);
            }
        });
    },
    
    /**
     * 단일 요소에 KaTeX 렌더링 적용
     * @param {HTMLElement} element - 렌더링할 요소
     */
    renderInElement(element) {
        let html = element.innerHTML;
        
        // Display mode ($$...$$)
        html = html.replace(/\$\$([\s\S]*?)\$\$/g, (match, latex) => {
            try {
                return katex.renderToString(latex, {
                    displayMode: true,
                    throwOnError: false
                });
            } catch (e) {
                console.warn("Display LaTeX 렌더링 실패:", latex, e);
                return match;
            }
        });
        
        // Inline mode ($...$)
        html = html.replace(/\$([\s\S]*?)\$/g, (match, latex) => {
            try {
                return katex.renderToString(latex, {
                    displayMode: false,
                    throwOnError: false
                });
            } catch (e) {
                console.warn("Inline LaTeX 렌더링 실패:", latex, e);
                return match;
            }
        });
        
        element.innerHTML = html;
    }
};