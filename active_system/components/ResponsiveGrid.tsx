import React from 'react';

interface ResponsiveGridProps {
  children: React.ReactNode;
  cols?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: number;
  className?: string;
}

export default function ResponsiveGrid({ 
  children, 
  cols = { sm: 1, md: 2, lg: 3, xl: 4 },
  gap = 4,
  className = ''
}: ResponsiveGridProps) {
  const gridCols = {
    sm: cols.sm || 1,
    md: cols.md || 2,
    lg: cols.lg || 3,
    xl: cols.xl || 4
  };

  const gridClasses = `
    grid gap-${gap}
    grid-cols-${gridCols.sm}
    md:grid-cols-${gridCols.md}
    lg:grid-cols-${gridCols.lg}
    xl:grid-cols-${gridCols.xl}
    ${className}
  `.trim();

  return (
    <div className={gridClasses}>
      {children}
    </div>
  );
}


