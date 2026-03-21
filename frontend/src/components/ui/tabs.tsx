import * as React from "react"

interface TabsProps {
  defaultValue?: string
  value?: string
  onValueChange?: (value: string) => void
  className?: string
  children?: React.ReactNode
}

export function Tabs({ defaultValue, value, onValueChange, className, children }: TabsProps) {
  const [internalValue, setInternalValue] = React.useState(defaultValue || "")
  const currentValue = value ?? internalValue

  const handleValueChange = (val: string) => {
    if (onValueChange) {
      onValueChange(val)
    } else {
      setInternalValue(val)
    }
  }

  return (
    <div className={className}>
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child

        // Check if child is one of our tab components
        const childType = (child as React.ReactElement).type
        const isTabComponent = (
          childType === TabsList ||
          childType === TabsTrigger ||
          childType === TabsContent ||
          (typeof childType === 'object' && childType !== null && (childType as any).displayName === 'TabsList') ||
          (typeof childType === 'object' && childType !== null && (childType as any).displayName === 'TabsTrigger') ||
          (typeof childType === 'object' && childType !== null && (childType as any).displayName === 'TabsContent')
        )

        if (isTabComponent) {
          return React.cloneElement(child as React.ReactElement<{ value?: string, onValueChange?: (v: string) => void }>, {
            value: currentValue,
            onValueChange: handleValueChange,
          })
        }

        // For non-tab components (like plain divs), just return as-is
        return child
      })}
    </div>
  )
}

interface TabsListProps {
  className?: string
  children?: React.ReactNode
}

export function TabsList({ className, children }: TabsListProps) {
  return (
    <div className={`inline-flex h-10 items-center justify-center ${className || ''}`}>
      {children}
    </div>
  )
}

interface TabsTriggerProps {
  value: string
  onValueChange?: (value: string) => void
  className?: string
  children?: React.ReactNode
}

export function TabsTrigger({ value, onValueChange, className, children }: TabsTriggerProps) {
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap px-3 py-1.5 text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 ${className || ''}`}
      onClick={() => onValueChange?.(value)}
    >
      {children}
    </button>
  )
}

interface TabsContentProps {
  value: string
  className?: string
  children?: React.ReactNode
}

export function TabsContent({ className, children }: TabsContentProps) {
  return (
    <div className={`mt-2 ${className || ''}`}>
      {children}
    </div>
  )
}
