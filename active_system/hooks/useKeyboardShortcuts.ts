import { useEffect } from 'react';

interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  action: () => void;
  description: string;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrl ? event.ctrlKey : !event.ctrlKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
}

// Predefined shortcuts for common actions
export const commonShortcuts: KeyboardShortcut[] = [
  {
    key: 'n',
    ctrl: true,
    action: () => console.log('New patient'),
    description: 'Yeni hasta ekle'
  },
  {
    key: 's',
    ctrl: true,
    action: () => console.log('Save'),
    description: 'Kaydet'
  },
  {
    key: 'f',
    ctrl: true,
    action: () => console.log('Search'),
    description: 'Ara'
  },
  {
    key: 'r',
    ctrl: true,
    action: () => console.log('Refresh'),
    description: 'Yenile'
  },
  {
    key: 'h',
    action: () => console.log('Help'),
    description: 'Yardım'
  },
  {
    key: 'Escape',
    action: () => console.log('Close modal'),
    description: 'Modal kapat'
  }
];


