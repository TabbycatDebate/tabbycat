import { getCurrentInstance } from 'vue'

export function useDjangoI18n () {
  const instance = getCurrentInstance()

  const globals = (typeof window !== 'undefined') ? window : globalThis
  const globalProperties = instance?.appContext?.config?.globalProperties

  const gettextImpl = globals?.gettext || globalProperties?.gettext
  const pgettextImpl = globals?.pgettext || globalProperties?.pgettext
  const ngettextImpl = globals?.ngettext || globalProperties?.ngettext
  const npgettextImpl = globals?.npgettext || globalProperties?.npgettext
  const pluralidxImpl = globals?.pluralidx || globalProperties?.pluralidx
  const interpolateImpl = globals?.interpolate || globalProperties?.interpolate

  const gettext = (...args) => (typeof gettextImpl === 'function' ? gettextImpl(...args) : undefined)
  const pgettext = (...args) => (typeof pgettextImpl === 'function' ? pgettextImpl(...args) : undefined)
  const ngettext = (...args) => (typeof ngettextImpl === 'function' ? ngettextImpl(...args) : undefined)
  const npgettext = (...args) => (typeof npgettextImpl === 'function' ? npgettextImpl(...args) : undefined)
  const pluralidx = (...args) => (typeof pluralidxImpl === 'function' ? pluralidxImpl(...args) : undefined)

  const tct = (text, variables) => {
    const fmt = gettext(text)
    if (typeof interpolateImpl === 'function') {
      return interpolateImpl(fmt, variables)
    }
    return fmt
  }

  return {
    gettext,
    pgettext,
    ngettext,
    npgettext,
    pluralidx,
    tct,
  }
}
