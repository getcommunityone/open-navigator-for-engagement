import { useState, useRef, useEffect } from 'react'
import { ChevronDownIcon, CheckIcon } from '@heroicons/react/24/outline'

interface MultiSelectProps {
  label: string
  options: { value: string; label: string; count?: number }[]
  selected: string[]
  onChange: (selected: string[]) => void
  placeholder?: string
  className?: string
}

export default function MultiSelect({
  label,
  options,
  selected,
  onChange,
  placeholder = 'Select...',
  className = ''
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggle = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter(v => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  const handleSelectAll = () => {
    onChange(options.map(opt => opt.value))
  }

  const handleDeselectAll = () => {
    onChange([])
  }

  const getDisplayText = () => {
    if (selected.length === 0) return placeholder
    if (selected.length === options.length) return 'All Selected'
    if (selected.length === 1) {
      const option = options.find(opt => opt.value === selected[0])
      return option?.label || selected[0]
    }
    return `${selected.length} selected`
  }

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      
      {/* Dropdown Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <span className={selected.length === 0 ? 'text-gray-500' : 'text-gray-900'}>
          {getDisplayText()}
        </span>
        <ChevronDownIcon className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full min-w-[300px] bg-white border border-gray-300 rounded-md shadow-lg max-h-80 overflow-auto">
          {/* Select All / Deselect All */}
          <div className="sticky top-0 bg-gray-50 border-b border-gray-200 px-3 py-2 flex gap-2">
            <button
              type="button"
              onClick={handleSelectAll}
              className="flex-1 text-xs font-medium text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50"
            >
              Select All
            </button>
            <button
              type="button"
              onClick={handleDeselectAll}
              className="flex-1 text-xs font-medium text-gray-600 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100"
            >
              Deselect All
            </button>
          </div>

          {/* Options */}
          <div className="py-1">
            {options.map((option) => {
              const isSelected = selected.includes(option.value)
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleToggle(option.value)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-gray-100 ${
                    isSelected ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <div className={`w-4 h-4 flex-shrink-0 border rounded flex items-center justify-center ${
                      isSelected 
                        ? 'bg-blue-600 border-blue-600' 
                        : 'border-gray-300'
                    }`}>
                      {isSelected && <CheckIcon className="h-3 w-3 text-white" />}
                    </div>
                    <span className={`truncate ${isSelected ? 'font-medium text-gray-900' : 'text-gray-700'}`} title={option.label}>
                      {option.label}
                    </span>
                  </div>
                  {option.count !== undefined && (
                    <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                      ({option.count.toLocaleString()})
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
