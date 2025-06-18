
import { Card } from "@/components/ui/card";

const RoastStyles = () => {
  const styles = [
    {
      name: "PackGod",
      emoji: "👑",
      description: "The OG roast master. Absolutely ruthless.",
      color: "from-red-600 to-red-800"
    },
    {
      name: "Gordon Ramsay",
      emoji: "👨‍🍳",
      description: "Kitchen nightmares meet Discord drama.",
      color: "from-orange-600 to-red-600"
    },
    {
      name: "Shakespeare",
      emoji: "🎭",
      description: "Elegant insults with old English flair.",
      color: "from-purple-600 to-indigo-600"
    },
    {
      name: "Anime Villain",
      emoji: "😈",
      description: "Over-the-top dramatic evil energy.",
      color: "from-pink-600 to-purple-600"
    },
    {
      name: "Drill Sergeant",
      emoji: "🪖",
      description: "Military-grade verbal destruction.",
      color: "from-green-600 to-green-800"
    },
    {
      name: "Karen",
      emoji: "💁‍♀️",
      description: "Passive-aggressive perfection.",
      color: "from-yellow-600 to-orange-600"
    }
  ];

  return (
    <div className="py-20 px-4 bg-gray-800/50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Choose Your Weapon 🔥
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Each persona brings their own flavor of destruction. Pick your fighter and watch the chaos unfold.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {styles.map((style, index) => (
            <Card 
              key={style.name}
              className="bg-gray-900 border-gray-700 hover:border-red-500 transition-all duration-300 transform hover:scale-105 cursor-pointer group"
            >
              <div className="p-6">
                <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${style.color} flex items-center justify-center text-2xl mb-4 group-hover:animate-pulse`}>
                  {style.emoji}
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{style.name}</h3>
                <p className="text-gray-400">{style.description}</p>
              </div>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-gray-400">
            <span className="text-red-500 font-semibold">Pro tip:</span> Use <code className="bg-gray-800 px-2 py-1 rounded text-red-400">/roast @username [style]</code> to get started
          </p>
        </div>
      </div>
    </div>
  );
};

export default RoastStyles;
