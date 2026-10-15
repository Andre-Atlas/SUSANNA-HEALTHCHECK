import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
// backdrop-filter (vidro) precisa da renderização com GPU emulada do Chrome
Config.setChromiumOpenGlRenderer('angle');
