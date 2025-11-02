import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';

interface LanguagePrioritySelectorProps {
  languages: Record<string, number>;
  selectedLanguage: string | null;
  onSelect: (language: string) => void;
}

export function LanguagePrioritySelector({
  languages,
  selectedLanguage,
  onSelect,
}: LanguagePrioritySelectorProps) {
  const sortedLanguages = Object.entries(languages)
    .sort(([, a], [, b]) => b - a);

  return (
    <RadioGroup value={selectedLanguage || ''} onValueChange={onSelect}>
      <div className="grid md:grid-cols-2 gap-3">
        {sortedLanguages.map(([lang, percentage]) => (
          <Card
            key={lang}
            className={`p-4 cursor-pointer transition-colors hover:bg-accent/50 ${
              selectedLanguage === lang ? 'border-primary bg-accent' : ''
            }`}
            onClick={() => onSelect(lang)}
          >
            <div className="flex items-center space-x-3">
              <RadioGroupItem value={lang} id={lang} />
              <div className="flex-1">
                <Label htmlFor={lang} className="cursor-pointer">
                  <div className="font-semibold">{lang}</div>
                  <div className="text-sm text-muted-foreground">
                    {percentage}% of codebase
                  </div>
                </Label>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </RadioGroup>
  );
}
