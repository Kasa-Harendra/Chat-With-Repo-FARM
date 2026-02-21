language_map = {
    # Programming Languages
    '.py': 'python',
    '.pyx': 'python',
    '.pyw': 'python',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.java': 'java',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.vb': 'vbnet',
    '.php': 'php',
    '.rb': 'ruby',
    '.rbw': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    '.dart': 'dart',
    '.r': 'r',
    '.R': 'r',
    '.m': 'matlab',
    '.pl': 'perl',
    '.pm': 'perl',
    '.lua': 'lua',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.erl': 'erlang',
    '.hrl': 'erlang',
    '.f': 'fortran',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.hs': 'haskell',
    '.lhs': 'haskell',
    '.jl': 'julia',
    '.clj': 'clojure',
    '.cljs': 'clojure',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.pas': 'pascal',
    '.pp': 'pascal',
    '.asm': 'assembly',
    '.s': 'assembly',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.xml': 'xml',
    '.xsl': 'xml',
    '.xsd': 'xml',
    '.ipynb': 'python Notebooks',
    '.svg': 'xml',
}

data_map = {    
    '.json': 'json',
    '.jsonl': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.csv': 'text',
    '.tsv': 'text',
    '.sql': 'sql'
}

documentation_map = {
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.rst': 'rst',
    '.txt': 'text',
    '.text': 'text',
}

configuration_map = {
    '.ini': 'ini',
    '.cfg': 'ini',
    '.conf': 'ini',
    '.env': 'bash',
    '.environment': 'bash',
    '.properties': 'properties',
    '.gitignore': 'text',
    '.gitattributes': 'text',
}

build_map = {
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'bash',
    '.bat': 'batch',
    '.cmd': 'batch',
    '.ps1': 'powershell',
}

additionals_map = {
    '.tex': 'latex',
    '.dockerfile': 'dockerfile',
    '.docker': 'dockerfile',
    '.makefile': 'makefile',
    '.mk': 'makefile',
    '.cmake': 'cmake',
    '.gradle': 'groovy',
    '.groovy': 'groovy',
    '.vim': 'vim',
    '.diff': 'diff',
    '.patch': 'diff',
    '.graphql': 'graphql',
    '.gql': 'graphql'
}

extension_map = language_map.copy()
extension_map.update(data_map)
extension_map.update(documentation_map)
extension_map.update(build_map)
extension_map.update(configuration_map)
extension_map.update(additionals_map)

# Categories for filtering
categories = {
    "Programming": list(language_map.keys()),
    "Data": list(data_map.keys()),
    "Documentation": list(documentation_map.keys()),
    "Configuration": list(configuration_map.keys()),
    "Build": list(build_map.keys()),
    "Additional": list(additionals_map.keys())
}
