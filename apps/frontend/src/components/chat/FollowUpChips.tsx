export function FollowUpChips({
  questions,
  onPick,
}: {
  questions: string[];
  onPick: (question: string) => void;
}) {
  if (questions.length === 0) return null;
  return (
    <div className="message-followups">
      <div className="followup-kicker">Follow-up questions</div>
      <div className="followup-grid">
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            className="followup-card"
            onClick={() => onPick(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
