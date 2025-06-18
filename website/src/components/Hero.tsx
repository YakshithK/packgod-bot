
import { Button } from "@/components/ui/button";
import { ExternalLink, Bot } from "lucide-react";

const Hero = () => {
  const handleAddToDiscord = () => {
    // Replace with actual Discord bot invite URL
    window.open('https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=2048&scope=bot', '_blank');
  };

  return (
    <div className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-red-900/20 via-gray-900 to-black"></div>
      
      <div className="relative max-w-6xl mx-auto px-4 py-20 text-center">
        {/* Bot Icon */}
        <div className="mb-8 flex justify-center">
          <div className="p-4 bg-red-600 rounded-full shadow-lg animate-pulse">
            <Bot className="w-12 h-12 text-white" />
          </div>
        </div>

        {/* Main Headline */}
        <h1 className="text-5xl md:text-7xl font-black mb-6 bg-gradient-to-r from-red-500 via-white to-red-500 bg-clip-text text-transparent animate-fade-in">
          PackGodBot
        </h1>
        
        {/* Tagline */}
        <p className="text-xl md:text-2xl text-gray-300 mb-8 font-medium animate-fade-in">
          💀 Get roasted by AI. Funniest Discord bot alive.
        </p>
        
        {/* Subtext */}
        <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto animate-fade-in">
          Unleash legendary roasts with AI-powered personas. From PackGod's savage burns to Gordon Ramsay's kitchen nightmares - your Discord will never be boring again.
        </p>

        {/* CTA Button */}
        <Button 
          onClick={handleAddToDiscord}
          className="bg-red-600 hover:bg-red-700 text-white font-bold text-lg px-8 py-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 animate-fade-in"
        >
          <ExternalLink className="w-5 h-5 mr-2" />
          ➕ Add to Discord
        </Button>

        {/* Stats */}
        <div className="mt-16 grid grid-cols-3 gap-8 max-w-md mx-auto">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">50K+</div>
            <div className="text-sm text-gray-400">Servers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">2M+</div>
            <div className="text-sm text-gray-400">Roasts Served</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">24/7</div>
            <div className="text-sm text-gray-400">Chaos</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
