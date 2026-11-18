import { Link } from 'react-router-dom'

/**
 * Breadcrumbs — navigation trail.
 * @param {Array<{label: string, href?: string}>} crumbs
 */
export default function Breadcrumbs({ crumbs = [] }) {
  if (crumbs.length === 0) return null

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <div className="container breadcrumbs__inner">
        {crumbs.map((crumb, index) => (
          <span key={index} className="breadcrumbs__item">
            {index > 0 && <span className="breadcrumbs__sep" aria-hidden="true">›</span>}
            {crumb.href ? (
              <Link to={crumb.href} className="breadcrumbs__link">{crumb.label}</Link>
            ) : (
              <span aria-current="page">{crumb.label}</span>
            )}
          </span>
        ))}
      </div>
    </nav>
  )
}
