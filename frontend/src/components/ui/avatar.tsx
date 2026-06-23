import * as React from 'react'
import { cn, stringToColor } from '@/lib/utils'

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  initials: string
  seed?: string
  size?: number
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ initials, seed, size = 36, className, style, ...props }, ref) => {
    const color = stringToColor(seed || initials)
    return (
      <div
        ref={ref}
        className={cn('flex items-center justify-center rounded-full font-bold shrink-0', className)}
        style={{
          width: size,
          height: size,
          fontSize: size * 0.38,
          color,
          backgroundColor: `${color}26`,
          border: `1.5px solid ${color}55`,
          ...style,
        }}
        {...props}
      >
        {initials}
      </div>
    )
  }
)
Avatar.displayName = 'Avatar'

export { Avatar }
