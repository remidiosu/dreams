import { ReactNode, useEffect } from 'react'
import { createPortal } from 'react-dom'

interface PageTitleProps {
  children: ReactNode
}

export function PageTitle({ children }: PageTitleProps) {
  useEffect(() => {
    document.title = `${typeof children === 'string' ? children : 'Page'} | Dream Journal`
  }, [children])

  const titleContainer = document.getElementById('page-title')
  if (!titleContainer) return null

  return createPortal(
    <h1 className="text-lg font-semibold text-foreground">{children}</h1>,
    titleContainer
  )
}