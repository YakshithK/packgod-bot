
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Check, Crown, Zap, Image } from "lucide-react";

const Premium = () => {
  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Brutal Mode",
      description: "Unlock the most savage roasts. No mercy."
    },
    {
      icon: <Image className="w-6 h-6" />,
      title: "Image Roasting",
      description: "Upload pics and get visually destroyed."
    },
    {
      icon: <Crown className="w-6 h-6" />,
      title: "Exclusive Styles",
      description: "Access premium personas like Eminem & more."
    }
  ];

  const handleBuyPremium = () => {
    // Replace with actual payment/premium URL
    window.open('https://your-payment-link.com', '_blank');
  };

  const handleJoinWaitlist = () => {
    // Replace with actual payment/premium URL
    window.open('https://forms.gle/FnitiAzhBsuYSVd97', '_blank');
  };

  return (
    <div className="py-20 px-4 bg-gradient-to-br from-gray-900 via-red-900/10 to-gray-900">
      <div className="max-w-4xl mx-auto text-center">
        <div className="mb-12">
          <Crown className="w-16 h-16 text-yellow-500 mx-auto mb-6 animate-bounce" />
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Go Premium 👑 (Coming Soon)
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Ready to take your roasting to the next level? Premium unlocks the most devastating features.
          </p>
        </div>

        <Card className="bg-gray-800 border-2 border-yellow-500/50 p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="bg-red-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-white">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">
              $4.99<span className="text-lg text-gray-400">/month</span>
            </div>
            <div className="text-gray-400 mb-6">Cancel anytime • No BS</div>
            <Button 
              onClick={handleJoinWaitlist}
              className="bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold text-lg px-8 py-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200"
            >
              📃 Join Waitlist Now!
            </Button>
            {/* <Button 
              onClick={handleBuyPremium}
              className="bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold text-lg px-8 py-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200"
            >
              💳 Buy Premium
            </Button> */}
          </div>
        </Card>

        <div className="flex items-center justify-center gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>30-day money back</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>Instant activation</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>Premium support</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Premium;
