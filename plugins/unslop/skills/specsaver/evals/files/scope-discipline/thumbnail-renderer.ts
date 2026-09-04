export interface SourceImageStore {
  read(assetId: string): Promise<Uint8Array | undefined>;
}

export interface ImageRenderer {
  render(
    source: Uint8Array,
    width: number,
    height: number,
  ): Promise<Uint8Array>;
}

export async function renderThumbnail(
  assetId: string,
  width: number,
  height: number,
  images: SourceImageStore,
  renderer: ImageRenderer,
): Promise<{ status: number; body?: Uint8Array }> {
  if (!Number.isInteger(width) || !Number.isInteger(height)) {
    return { status: 400 };
  }

  if (width < 1 || height < 1 || width > 4096 || height > 4096) {
    return { status: 400 };
  }

  const source = await images.read(assetId);
  if (source === undefined) {
    return { status: 404 };
  }

  return { status: 200, body: await renderer.render(source, width, height) };
}
