const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

class Logger {
  private source: string

  constructor(source: string = 'app') {
    this.source = source
  }

  private async log(level: LogLevel, message: string, data?: unknown) {
    const fullMessage = data ? `${message} ${JSON.stringify(data)}` : message

    // Console output
    const consoleMsg = `[${this.source}] ${message}`
    switch (level) {
      case 'debug':
        console.debug(consoleMsg, data ?? '')
        break
      case 'info':
        console.info(consoleMsg, data ?? '')
        break
      case 'warn':
        console.warn(consoleMsg, data ?? '')
        break
      case 'error':
        console.error(consoleMsg, data ?? '')
        break
    }

    // Send to backend
    try {
      await fetch(`${API_BASE_URL}/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level,
          message: fullMessage,
          source: this.source,
        }),
      })
    } catch {
      // Ignore logging errors
    }
  }

  debug(message: string, data?: unknown) {
    this.log('debug', message, data)
  }

  info(message: string, data?: unknown) {
    this.log('info', message, data)
  }

  warn(message: string, data?: unknown) {
    this.log('warn', message, data)
  }

  error(message: string, data?: unknown) {
    this.log('error', message, data)
  }
}

export const logger = new Logger('frontend')

export function createLogger(source: string) {
  return new Logger(source)
}
