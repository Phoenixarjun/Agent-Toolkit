export const MANAGED_START_MARKER = '<!-- BEGIN AGENT-TOOLKIT MANAGED BLOCK -->';
export const MANAGED_END_MARKER = '<!-- END AGENT-TOOLKIT MANAGED BLOCK -->';

export function mergeManagedEntrypointFile(existingContent, managedBlock, isCursorMdc = false) {
  if (existingContent === null || existingContent === undefined) {
    if (isCursorMdc) {
      return (
        '---\n' +
        'description: Agent Toolkit integration and active capabilities\n' +
        'globs: *\n' +
        'alwaysApply: true\n' +
        '---\n\n' +
        managedBlock +
        '\n'
      );
    }
    return managedBlock + '\n';
  }

  const text = String(existingContent);
  if (text.includes(MANAGED_START_MARKER) && text.includes(MANAGED_END_MARKER)) {
    const startIndex = text.indexOf(MANAGED_START_MARKER);
    const endIndex = text.indexOf(MANAGED_END_MARKER) + MANAGED_END_MARKER.length;
    return text.substring(0, startIndex) + managedBlock + text.substring(endIndex);
  }

  // Prepend block, preserving frontmatter if present
  if (text.startsWith('---\n')) {
    const endFm = text.indexOf('\n---\n', 4);
    if (endFm !== -1) {
      const frontmatter = text.substring(0, endFm + 5);
      const rest = text.substring(endFm + 5).trimStart();
      return frontmatter + '\n' + managedBlock + '\n\n' + rest;
    }
  }

  return managedBlock + '\n\n' + text.trimStart();
}
