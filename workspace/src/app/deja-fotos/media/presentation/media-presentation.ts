/*
 * Deja Fotos
 *
 * Media Presentation Helpers
 */

import {
  MediaOriginalDatePrecision,
  MediaOriginalDateSource,
  MediaProcessingStatus,
  MediaType,
} from '../domain';

export const MEDIA_TYPE_LABELS: Readonly<Record<MediaType, string>> = {
  image: 'Imagem',
  video: 'Vídeo',
};

export const MEDIA_PROCESSING_STATUS_LABELS:
  Readonly<Record<MediaProcessingStatus, string>> = {
    received: 'Recebida',
    validating: 'Validando',
    processing: 'Processando',
    ready: 'Pronta',
    failed: 'Falhou',
    quarantine: 'Quarentena',
  };

export const MEDIA_ORIGINAL_DATE_SOURCE_LABELS:
  Readonly<Record<MediaOriginalDateSource, string>> = {
    embedded_metadata: 'Metadados internos',
    source_folder: 'Pasta de origem',
    filename: 'Nome do arquivo',
    filesystem: 'Sistema de arquivos',
    manual: 'Correção manual',
    ai_suggested: 'Sugestão da IA',
  };

export function formatMediaDate(
  value: string | null,
  precision: MediaOriginalDatePrecision | null,
): string {
  if (!value) {
    return 'Sem data';
  }

  if (precision === 'date') {
    const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(
      value,
    );

    if (!match) {
      return 'Data inválida';
    }

    const [
      ,
      year,
      month,
      day,
    ] = match;

    return `${day}/${month}/${year} — horário desconhecido`;
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return 'Data inválida';
  }

  return new Intl.DateTimeFormat(
    'pt-BR',
    {
      dateStyle: 'short',
      timeStyle: 'short',
    },
  ).format(date);
}

export function formatMediaFileSize(
  value: number,
): string {
  if (value < 1024) {
    return `${value} B`;
  }

  const units = [
    'KB',
    'MB',
    'GB',
    'TB',
  ];

  let size = value / 1024;
  let unitIndex = 0;

  while (
    size >= 1024
    && unitIndex < units.length - 1
  ) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toLocaleString(
    'pt-BR',
    {
      maximumFractionDigits: 1,
    },
  )} ${units[unitIndex]}`;
}

export function formatMediaDuration(
  value: number | null,
): string | null {
  if (value === null) {
    return null;
  }

  const totalSeconds = Math.max(
    0,
    Math.round(value),
  );

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts = [
    minutes.toString().padStart(2, '0'),
    seconds.toString().padStart(2, '0'),
  ];

  if (hours > 0) {
    parts.unshift(hours.toString());
  }

  return parts.join(':');
}