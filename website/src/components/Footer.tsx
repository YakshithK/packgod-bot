
const Footer = () => {
  return (
    <footer className="bg-black py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-bold text-white mb-4">PackGodBot</h3>
            <p className="text-gray-400">
              The ultimate Discord roasting experience. Built by degenerates, for degenerates.
            </p>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-red-500 transition-colors">Commands</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">Support Server</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">Terms of Service</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Community</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-red-500 transition-colors">Discord Server</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">Twitter</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">Reddit</a></li>
              <li><a href="#" className="hover:text-red-500 transition-colors">GitHub</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 pt-8 text-center">
          <p className="text-gray-400">
            © 2024 PackGodBot. All rights reserved. No feelings were spared in the making of this bot.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
