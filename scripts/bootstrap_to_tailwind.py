#!/usr/bin/env python3
from pathlib import Path
import re

CLASS_MAP = {
    'container-fluid': 'w-full px-4',
    'container': 'mx-auto px-4',
    'row': 'flex flex-wrap -mx-3',
    'col': 'w-full px-3',
    'col-12': 'w-full px-3',
    'col-6': 'w-1/2 px-3',
    'col-md-6': 'md:w-1/2 px-3',
    'col-md-4': 'md:w-1/3 px-3',
    'col-md-3': 'md:w-1/4 px-3',
    'col-sm-6': 'sm:w-1/2 px-3',
    'd-flex': 'flex',
    'd-inline-block': 'inline-block',
    'd-block': 'block',
    'd-none': 'hidden',
    'justify-content-between': 'justify-between',
    'justify-content-center': 'justify-center',
    'justify-content-end': 'justify-end',
    'align-items-center': 'items-center',
    'align-items-start': 'items-start',
    'text-center': 'text-center',
    'text-right': 'text-right',
    'text-left': 'text-left',
    'text-white': 'text-white',
    'text-dark': 'text-gray-900',
    'text-danger': 'text-red-600',
    'text-success': 'text-green-600',
    'bg-white': 'bg-white',
    'bg-danger': 'bg-red-600',
    'bg-primary': 'bg-blue-600',
    'bg-success': 'bg-green-600',
    'bg-warning': 'bg-yellow-500',
    'bg-light': 'bg-gray-100',
    'mt-0': 'mt-0',
    'mt-1': 'mt-1',
    'mt-2': 'mt-2',
    'mt-3': 'mt-3',
    'mt-4': 'mt-4',
    'mt-5': 'mt-5',
    'mb-0': 'mb-0',
    'mb-1': 'mb-1',
    'mb-2': 'mb-2',
    'mb-3': 'mb-3',
    'mb-4': 'mb-4',
    'mb-5': 'mb-5',
    'ml-auto': 'ml-auto',
    'mr-2': 'mr-2',
    'mr-3': 'mr-3',
    'mr-4': 'mr-4',
    'p-0': 'p-0',
    'p-2': 'p-2',
    'p-3': 'p-3',
    'p-4': 'p-4',
    'px-0': 'px-0',
    'px-2': 'px-2',
    'px-3': 'px-3',
    'py-2': 'py-2',
    'py-3': 'py-3',
    'w-100': 'w-full',
    'h-100': 'h-full',
    'btn': 'inline-flex items-center justify-center rounded px-4 py-2 font-medium transition-colors',
    'btn-sm': 'text-sm px-3 py-1.5',
    'btn-lg': 'text-lg px-5 py-3',
    'btn-primary': 'bg-blue-600 text-white hover:bg-blue-700',
    'btn-secondary': 'bg-gray-600 text-white hover:bg-gray-700',
    'btn-success': 'bg-green-600 text-white hover:bg-green-700',
    'btn-danger': 'bg-red-600 text-white hover:bg-red-700',
    'btn-warning': 'bg-yellow-500 text-gray-900 hover:bg-yellow-600',
    'btn-info': 'bg-cyan-600 text-white hover:bg-cyan-700',
    'btn-light': 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    'btn-dark': 'bg-gray-900 text-white hover:bg-black',
    'btn-link': 'text-blue-600 hover:text-blue-700 underline',
    'form-control': 'block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500',
    'form-select': 'block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500',
    'form-check-input': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500',
    'form-check-label': 'ml-2 text-sm text-gray-700',
    'table': 'min-w-full divide-y divide-gray-200',
    'table-responsive': 'overflow-x-auto',
    'card': 'rounded-lg border border-gray-200 bg-white shadow-sm',
    'card-body': 'p-4',
    'card-header': 'px-4 py-3 border-b border-gray-200',
    'card-footer': 'px-4 py-3 border-t border-gray-200',
    'badge': 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
    'badge-danger': 'bg-red-100 text-red-700',
    'badge-success': 'bg-green-100 text-green-700',
    'badge-warning': 'bg-yellow-100 text-yellow-700',
    'badge-primary': 'bg-blue-100 text-blue-700',
    'dropdown-menu': 'z-50 mt-2 min-w-[12rem] rounded-md border border-gray-200 bg-white py-1 shadow-lg',
    'dropdown-item': 'block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100',
    'nav': 'flex flex-wrap',
    'nav-item': 'list-none',
    'nav-link': 'inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600',
    'rounded-circle': 'rounded-full',
}

files = [p for p in Path('.').rglob('*.html') if '.git' not in p.parts]
for path in files:
    text = path.read_text(encoding='utf-8')
    original = text
    text = text.replace('{% load django_bootstrap5 %}', '')
    text = re.sub(r'\{\%\s*bootstrap_css\s*\%\}\s*', '', text)
    text = re.sub(r'\{\%\s*bootstrap_javascript\s*\%\}\s*', '', text)

    def repl(m):
        classes = m.group(1).split()
        out = []
        for c in classes:
            mapped = CLASS_MAP.get(c, c)
            out.extend(mapped.split())
        dedup = []
        for c in out:
            if c not in dedup:
                dedup.append(c)
        return 'class="' + ' '.join(dedup) + '"'

    text = re.sub(r'class="([^"]+)"', repl, text)
    if text != original:
        path.write_text(text, encoding='utf-8')

print(f"Processed {len(files)} html files")
