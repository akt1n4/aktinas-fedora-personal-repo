%global __provides_exclude_from ^%{_libdir}/(%{name}|lv2)/.*$
%global __requires_exclude ^lib(aaf|alsa_audiobackend|ardour.*|audiographer|canvas|dummy_audiobackend|evoral|gtkmm2ext|jack_audiobackend|midipp|pan[12]in2out|panbalance|panvbap|pbd|ptformat|pulseaudio_backend.so|qmdsp|suil|temporal|timecode|waveview|widgets|ydk|ydk-pixbuf|ydkmm|ytk|ytkmm|ztk|ztkmm)\.so.*$

Name:           ardour9
Version:        9.7
Release:        1%{?dist}
Summary:        Professional-grade digital audio workstation
# Mapped from Arch's license array
License:        GPL-2.0-or-later AND GPL-3.0-or-later AND MIT AND CC0-1.0
URL:            https://ardour.org/

Source0:        https://github.com/Ardour/ardour/archive/%{version}/ardour-%{version}.tar.gz
Patch0:         ardour-7.0-re-vendor_qm-dsp.patch

BuildRequires:  gcc-c++
BuildRequires:  python3
BuildRequires:  git
BuildRequires:  doxygen
BuildRequires:  graphviz
BuildRequires:  itstool
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Adopted from Arch's makedepends/depends using clean Fedora pkgconfig names
BuildRequires:  boost-devel
BuildRequires:  readline-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(aubio)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairomm-1.0)
BuildRequires:  pkgconfig(cppunit)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(fftw3f)
BuildRequires:  pkgconfig(flac)
BuildRequires:  pkgconfig(fluidsynth)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(glibmm-2.4)
BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(liblo)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(libwebsockets)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(lilv-0)
BuildRequires:  pkgconfig(lrdf)
BuildRequires:  pkgconfig(ltc)
BuildRequires:  pkgconfig(lv2)
BuildRequires:  pkgconfig(ogg)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangomm-1.4)
BuildRequires:  pkgconfig(rubberband)
BuildRequires:  pkgconfig(samplerate)
BuildRequires:  pkgconfig(serd-0)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(sord-0)
BuildRequires:  pkgconfig(sratom-0)
BuildRequires:  pkgconfig(vamp-plugin-sdk)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xext)

# Bundled libraries per Fedora guidelines
Provides:       bundled(gtk-theme-engine-clearlooks) = 2.9.0
Provides:       bundled(libsmf) = 1.2
Provides:       bundled(lua) = 5.3.5
Provides:       bundled(LuaBridge) = 1.0.2
Provides:       bundled(midi++) = 4.1.0
Provides:       bundled(pbd) = 4.1.0
Provides:       bundled(ytk) = 2.24.23
Provides:       bundled(ydk) = 2.24.23
Provides:       bundled(ytkmm) = 2.24.5
Provides:       bundled(ydkmm) = 2.24.5
Provides:       bundled(ydk-pixbuf) = 2.31.1
Provides:       bundled(suil) = 0.10.8
Provides:       bundled(ztk) = 2.14.0
Provides:       bundled(ztkmm) = 2.22.7

Requires:       hicolor-icon-theme

# Optdepends functionality in Fedora
Recommends:     harvid
Recommends:     xjadeo
Recommends:     new-session-manager

%description
Ardour is a multi-channel digital audio workstation, allowing users to record,
edit, mix and master audio and MIDI projects. It is targeted at audio
engineers, musicians, soundtrack editors and composers.

%prep
%autosetup -n ardour-%{version} -p1

# Unsetting gtk2 rc (FS#54389)
sed -e '8iexport GTK2_RC_FILES=/dev/null' -i gtk2_ardour/ardour.sh.in

# Arch fixes to use system waf/includes
touch __init__.py
sed -e "s/('misc')/('misc', tooldir='tools')/" \
    -i {gtk2_ardour,headless,luasession,session_utils,libs/fst}/wscript
find . -type f -iname "*wscript*" \
    -exec sed -e 's/from waflib.extras import autowaf/from tools import autowaf/g' \
              -e 's/import waflib.extras.autowaf/from tools import autowaf/g' \
              -i {} \;

# Remove system-provided libraries to force external use
for i in fluidsynth hidapi libltc qm-dsp; do
    find "libs/$i" \( -name \*.\[ch\] -o -name \*.cc -o -name \*.\[ch\]pp \) -delete
done

%build
%set_build_flags
export LINKFLAGS="%{__global_ldflags}"

# Execute waf with parameters mirroring the Arch configure array
./waf configure \
    --prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --configdir=%{_sysconfdir} \
    --datadir=%{_datadir} \
    --includedir=%{_includedir} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --cxx17 \
    --freedesktop \
    --no-phone-home \
    --optimize \
    --ptformat \
    --use-external-libs \
    --with-backends="alsa,dummy,jack,pulseaudio"

./waf build -v %{?_smp_mflags}

%install
./waf i18n --destdir=%{buildroot}
./waf install --destdir=%{buildroot}

# Install man page
install -vDm 644 ardour.1 -t %{buildroot}%{_mandir}/man1/

# Move appdata and metainfo to the proper Fedora location
mkdir -p %{buildroot}%{_metainfodir}
mv %{buildroot}%{_datadir}/{appdata,metainfo}/*.xml %{buildroot}%{_metainfodir}/ 2>/dev/null || true

# Desktop and AppStream Validation
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    --set-key=Name --set-value="Ardour %{version}" \
    %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml

# Find translation files
%find_lang %{name}
%find_lang gtk2_%{name}
%find_lang gtkmm2ext3
%find_lang ytk9

%files -f %{name}.lang -f gtk2_%{name}.lang -f gtkmm2ext3.lang -f ytk9.lang
%license COPYING
%doc README.md
%config(noreplace) %{_sysconfdir}/%{name}/
%{_bindir}/%{name}
%{_bindir}/%{name}-export
%{_bindir}/%{name}-lua
%{_bindir}/%{name}-new_empty_session
%{_bindir}/%{name}-new_session
%{_libdir}/%{name}/
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/mime/packages/ardour.xml
%{_metainfodir}/*.xml
%{_mandir}/man1/%{name}.1*
