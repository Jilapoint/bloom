/**
 * BloomLogo — the lotus icon used as Bloom's visual identity.
 *
 * Renders the PNG located at /public/bloom-logo.png.
 * Use `size` to match surrounding text or container — defaults to 22px.
 * The PNG already has a rose-tinted circular background, so callers
 * generally should NOT wrap it in another colored container.
 */
export default function BloomLogo({ size = 22, className = '', alt = 'Bloom', ...props }) {
  return (
    <img
      src="/bloom-logo.png"
      alt={alt}
      width={size}
      height={size}
      className={className}
      style={{
        objectFit: 'contain',
        display: 'block',
        ...props.style,
      }}
      {...props}
    />
  );
}
