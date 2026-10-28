export function replySpeakerOptions (options, restrictReplySpeaker, isReplySpeaker, disallowedReplySpeaker) {
  const filteredOptions = restrictReplySpeaker && isReplySpeaker && disallowedReplySpeaker
    ? options.filter(option => option.value !== disallowedReplySpeaker)
    : options
  return filteredOptions.sort((a, b) => a.text.localeCompare(b.text))
}
