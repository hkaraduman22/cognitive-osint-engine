unit USecureStorage;

interface

uses
  System.SysUtils;

type
  /// <summary>
  /// Windows DPAPI (CryptProtectData/CryptUnprotectData) kullanarak refresh token'i
  /// mevcut Windows kullanicisina baglayarak sifreler ve diskte saklar. Sifreleme
  /// anahtari Windows tarafindan yonetildigi icin dosyanin kendisi baska bir
  /// bilgisayara/kullaniciya tasinirsa cozulemez.
  /// </summary>
  TSecureStorage = class
  private
    class function Protect(const APlainText: string): TBytes; static;
    class function Unprotect(const AProtectedData: TBytes): string; static;
    class function GetSessionFilePath: string; static;
  public
    /// <summary>Kullanici adi + refresh token'i tek bir JSON zarfi olarak sifreleyip yazar.</summary>
    class procedure SaveSession(const AUsername, ARefreshToken: string); static;
    /// <summary>Kayitli oturumu okur. Bulunamazsa/bozuksa False doner.</summary>
    class function LoadSession(out AUsername, ARefreshToken: string): Boolean; static;
    class procedure ClearSession; static;
  end;

implementation

uses
  Winapi.Windows,
  Winapi.Wincrypt,
  System.IOUtils,
  System.JSON;

class function TSecureStorage.Protect(const APlainText: string): TBytes;
var
  LInputBlob, LOutputBlob: DATA_BLOB;
  LPlainBytes: TBytes;
begin
  LPlainBytes := TEncoding.UTF8.GetBytes(APlainText);
  if Length(LPlainBytes) = 0 then
    Exit(nil);

  LInputBlob.cbData := Length(LPlainBytes);
  LInputBlob.pbData := @LPlainBytes[0];
  FillChar(LOutputBlob, SizeOf(LOutputBlob), 0);

  if not CryptProtectData(@LInputBlob, 'OsintFrontendSession', nil, nil, nil,
    CRYPTPROTECT_UI_FORBIDDEN, @LOutputBlob) then
    raise Exception.CreateFmt('DPAPI sifreleme basarisiz. Hata kodu: %d', [GetLastError]);

  try
    SetLength(Result, LOutputBlob.cbData);
    if LOutputBlob.cbData > 0 then
      Move(LOutputBlob.pbData^, Result[0], LOutputBlob.cbData);
  finally
    LocalFree(HLOCAL(LOutputBlob.pbData));
  end;
end;

class function TSecureStorage.Unprotect(const AProtectedData: TBytes): string;
var
  LInputBlob, LOutputBlob: DATA_BLOB;
  LPlainBytes: TBytes;
begin
  if Length(AProtectedData) = 0 then
    Exit('');

  LInputBlob.cbData := Length(AProtectedData);
  LInputBlob.pbData := @AProtectedData[0];
  FillChar(LOutputBlob, SizeOf(LOutputBlob), 0);

  if not CryptUnprotectData(@LInputBlob, nil, nil, nil, nil, CRYPTPROTECT_UI_FORBIDDEN, @LOutputBlob) then
    raise Exception.CreateFmt('DPAPI sifre cozme basarisiz. Hata kodu: %d', [GetLastError]);

  try
    SetLength(LPlainBytes, LOutputBlob.cbData);
    if LOutputBlob.cbData > 0 then
      Move(LOutputBlob.pbData^, LPlainBytes[0], LOutputBlob.cbData);
    Result := TEncoding.UTF8.GetString(LPlainBytes);
  finally
    LocalFree(HLOCAL(LOutputBlob.pbData));
  end;
end;

class function TSecureStorage.GetSessionFilePath: string;
var
  LAppDataDir: string;
begin
  LAppDataDir := TPath.Combine(GetEnvironmentVariable('APPDATA'), 'OsintFrontend');
  if not TDirectory.Exists(LAppDataDir) then
    TDirectory.CreateDirectory(LAppDataDir);
  Result := TPath.Combine(LAppDataDir, 'session.dat');
end;

class procedure TSecureStorage.SaveSession(const AUsername, ARefreshToken: string);
var
  LEnvelope: TJSONObject;
begin
  if Trim(ARefreshToken) = '' then
  begin
    ClearSession;
    Exit;
  end;

  LEnvelope := TJSONObject.Create;
  try
    LEnvelope.AddPair('username', AUsername);
    LEnvelope.AddPair('refresh_token', ARefreshToken);
    TFile.WriteAllBytes(GetSessionFilePath, Protect(LEnvelope.ToJSON));
  finally
    LEnvelope.Free;
  end;
end;

class function TSecureStorage.LoadSession(out AUsername, ARefreshToken: string): Boolean;
var
  LFilePath: string;
  LPlainText: string;
  LJsonValue: TJSONValue;
  LUsernameValue, LRefreshValue: TJSONValue;
begin
  AUsername := '';
  ARefreshToken := '';
  Result := False;

  LFilePath := GetSessionFilePath;
  if not TFile.Exists(LFilePath) then
    Exit;

  try
    LPlainText := Unprotect(TFile.ReadAllBytes(LFilePath));
    LJsonValue := TJSONObject.ParseJSONValue(LPlainText);
    try
      if not (LJsonValue is TJSONObject) then
        Exit;

      LUsernameValue := TJSONObject(LJsonValue).GetValue('username');
      if Assigned(LUsernameValue) then
        AUsername := LUsernameValue.Value;

      LRefreshValue := TJSONObject(LJsonValue).GetValue('refresh_token');
      if Assigned(LRefreshValue) then
        ARefreshToken := LRefreshValue.Value;

      Result := ARefreshToken <> '';
    finally
      LJsonValue.Free;
    end;
  except
    // Bozuk/gecersiz/baska kullaniciya ait dosya - sessizce temizle,
    // normal login akisina dusulmesini sagla.
    ClearSession;
    Result := False;
  end;
end;

class procedure TSecureStorage.ClearSession;
var
  LFilePath: string;
begin
  LFilePath := GetSessionFilePath;
  if TFile.Exists(LFilePath) then
    TFile.Delete(LFilePath);
end;

end.
