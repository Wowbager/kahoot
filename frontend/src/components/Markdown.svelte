<script>
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  export let content = '';
  $: html = DOMPurify.sanitize(marked.parse(content || ''));
</script>

<div class="markdown">{@html html}</div>

<style>
  .markdown { line-height: 1.7; }
  .markdown :global(h1) { font-size: 2.5rem; margin-bottom: 1rem; }
  .markdown :global(h2) { font-size: 1.8rem; margin-bottom: 0.8rem; }
  .markdown :global(h3) { font-size: 1.4rem; margin-bottom: 0.6rem; }
  .markdown :global(p)  { margin-bottom: 0.8rem; }
  .markdown :global(ul), .markdown :global(ol) { margin-left: 1.5rem; margin-bottom: 0.8rem; }
  .markdown :global(blockquote) {
    border-left: 4px solid #7c3aed;
    padding-left: 1rem;
    margin: 1rem 0;
    color: #ccc;
    font-style: italic;
  }
  .markdown :global(code) {
    background: rgba(255,255,255,0.1);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
  }
  .markdown :global(hr) { border: none; border-top: 1px solid rgba(255,255,255,0.2); margin: 1.5rem 0; }
  .markdown :global(strong) { color: #fff; }
</style>
