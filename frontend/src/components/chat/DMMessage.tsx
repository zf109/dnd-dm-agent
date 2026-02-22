import ReactMarkdown from 'react-markdown';

interface Props {
  content: string;
  isComplete: boolean;
}

export function DMMessage({ content, isComplete }: Props) {
  return (
    <div className={`dm-message ${!isComplete ? 'streaming' : ''}`}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
