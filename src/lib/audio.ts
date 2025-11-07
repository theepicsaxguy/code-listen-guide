export function decodeBase64Audio(input: string): Uint8Array {
  const normalized = input.replace(/\s/g, "");
  const binary = atob(normalized);
  const length = binary.length;
  const bytes = new Uint8Array(length);
  for (let index = 0; index < length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

export async function decodePcmToAudioBuffer(
  data: Uint8Array,
  context: AudioContext,
  sampleRate: number,
  channels: number,
): Promise<AudioBuffer> {
  const typed = new Int16Array(data.buffer.slice(0));
  const frameCount = typed.length / channels;
  const buffer = context.createBuffer(channels, frameCount, sampleRate);
  for (let channel = 0; channel < channels; channel += 1) {
    const channelData = buffer.getChannelData(channel);
    for (let frame = 0; frame < frameCount; frame += 1) {
      channelData[frame] = typed[frame * channels + channel] / 32768;
    }
  }
  return buffer;
}
