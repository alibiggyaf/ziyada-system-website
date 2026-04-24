export default function GlassPanel({ children, style = {}, className = '', onMouseEnter, onMouseLeave }) {
  return (
    <div
      className={`glass-panel ${className}`}
      style={style}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {children}
    </div>
  );
}