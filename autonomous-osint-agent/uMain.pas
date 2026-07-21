unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls,
  System.Threading, System.JSON, System.Generics.Collections, Vcl.ExtCtrls, Winapi.ShellAPI,
  Vcl.ComCtrls;

type
  TfrmMain = class(TForm)
    pnlLogin: TPanel;
    pnlLoginBox: TPanel;
    lblLoginTitle: TLabel;
    edtUsername: TEdit;
    edtPassword: TEdit;
    btnLogin: TButton;
    btnRegister: TButton;
    
    pgcMain: TPageControl;
    tsRecherche: TTabSheet;
    tsIstatistik: TTabSheet;
    tsLoglar: TTabSheet;

    pnlFiltreler: TPanel;
    lblFiltreBaslik: TLabel;
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    edtUnvan: TEdit;
    cmbCalisanSayisi: TComboBox;
    chkSadeceYatirimAlanlar: TCheckBox;
    btnAra: TButton;
    lblBotBaslik: TLabel;
    btnTaramaBaslat: TButton;
    
    dbgSonuclar: TDBGrid;
    
    pnlIstatistikTop: TPanel;
    btnAnalizGetir: TButton;
    mmoIstatistik: TMemo;

    mmoLoglar: TMemo;

    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;

    RestReqStats: TRESTRequest;
    RestResStats: TRESTResponse;

    procedure btnAraClick(Sender: TObject);
    procedure btnTaramaBaslatClick(Sender: TObject);
    procedure btnAnalizGetirClick(Sender: TObject);
    procedure dbgSonuclarDblClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnLoginClick(Sender: TObject);
    procedure btnRegisterClick(Sender: TObject);
  private
    procedure GelismisAramaYap;
    procedure LogYaz(AMesaj: string);
  public
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.LogYaz(AMesaj: string);
begin
  mmoLoglar.Lines.Add(FormatDateTime('hh:nn:ss', Now) + ' [SYS] > ' + AMesaj);
end;

procedure TfrmMain.FormCreate(Sender: TObject);
var
  ProjectRootDir: string;
  BatchScriptPath: string;
begin
  // Initialize Comboboxes
  if cmbSektor.Items.Count = 0 then
  begin
    cmbSektor.Items.Add('T' + #252 + 'm' + #252);
    cmbSektor.Items.Add('Yaz' + #305 + 'l' + #305 + 'm');
    cmbSektor.Items.Add('Otomotiv');
    cmbSektor.Items.Add('Tekstil');
    cmbSektor.Items.Add('G' + #305 + 'da');
    cmbSektor.Items.Add('Savunma');
  end;
  cmbSektor.ItemIndex := 0;

  if cmbCalisanSayisi.Items.Count = 0 then
  begin
    cmbCalisanSayisi.Items.Add('T' + #252 + 'm' + #252);
    cmbCalisanSayisi.Items.Add('1-50');
    cmbCalisanSayisi.Items.Add('50-250');
    cmbCalisanSayisi.Items.Add('250+');
  end;
  cmbCalisanSayisi.ItemIndex := 0;

  // Initialize UI State
  pnlLogin.Visible := True;
  pgcMain.Visible := False;
  pgcMain.ActivePageIndex := 0;
  
  LogYaz('Sistem ba' + #351 + 'lat' + #305 + 'ld' + #305 + '. Kimlik do' + #287 + 'rulamas' + #305 + ' bekleniyor.');

  // Launch Backend automatically via the unified start_services.bat
  ProjectRootDir := ExpandFileName(ExtractFilePath(Application.ExeName) + '..\');
  BatchScriptPath := ProjectRootDir + 'start_services.bat';

  // FIX DBGrid: Prevent Delphi from treating the JSON array as a nested dataset
  RestAdapter.NestedElements := False;
  RestAdapter.RootElement := ''; // Process the root JSON array directly

  if FileExists(BatchScriptPath) then
  begin
    ShellExecute(0, 'open', PChar(BatchScriptPath), nil, PChar(ProjectRootDir), SW_SHOWNORMAL);
    LogYaz('Arka plan Docker ve FastAPI servisleri tetiklendi. L' + #252 + 'tfen birka' + #231 + ' saniye bekleyin...');
  end
  else
  begin
    LogYaz('[UYARI] start_services.bat bulunamad' + #305 + ': ' + BatchScriptPath);
  end;
end;

procedure TfrmMain.btnLoginClick(Sender: TObject);
var
  JSONPayload: TJSONObject;
begin
  if (Trim(edtUsername.Text) = '') or (Trim(edtPassword.Text) = '') then
  begin
    ShowMessage('L' + #252 + 'tfen kullan' + #305 + 'c' + #305 + ' ad' + #305 + ' ve ' + #351 + 'ifre giriniz.');
    Exit;
  end;

  RestRequest.Params.Clear;
  RestRequest.Method := rmPOST;
  RestRequest.Resource := 'auth/login';

  JSONPayload := TJSONObject.Create;
  try
    JSONPayload.AddPair('username', Trim(edtUsername.Text));
    JSONPayload.AddPair('password', Trim(edtPassword.Text));
    RestRequest.AddBody(JSONPayload);

    try
      RestRequest.Execute;

      if RestResponse.StatusCode = 200 then
      begin
        LogYaz('Oturum A' + #231 + 'ma Ba' + #351 + 'ar' + #305 + 'l' + #305 + '. API eri' + #351 + 'im yetkisi al' + #305 + 'nd' + #305 + '.');
        pnlLogin.Visible := False;
        pgcMain.Visible := True;
        GelismisAramaYap; // Auto-fetch on login
      end
      else
      begin
        ShowMessage('Hatal' + #305 + ' kullan' + #305 + 'c' + #305 + ' ad' + #305 + ' veya ' + #351 + 'ifre!');
        LogYaz('[UYARI] Kimlik do' + #287 + 'rulama ba' + #351 + 'ar' + #305 + 's' + #305 + 'z.');
      end;
    except
      on E: Exception do
      begin
        ShowMessage('Sunucu ba' + #287 + 'lant' + #305 + 's' + #305 + ' kurulamad' + #305 + '. L' + #252 + 'tfen Docker ve FastAPI''nin ba' + #351 + 'lamas' + #305 + 'n' + #305 + ' bekleyip tekrar deneyin.' + #13#10 + E.Message);
        LogYaz('[HATA] Ba' + #287 + 'lant' + #305 + ' hatas' + #305 + ': ' + E.Message);
      end;
    end;
  finally
    RestRequest.Params.Clear;
  end;
end;

procedure TfrmMain.btnRegisterClick(Sender: TObject);
var
  JSONPayload: TJSONObject;
begin
  if (Trim(edtUsername.Text) = '') or (Trim(edtPassword.Text) = '') then
  begin
    ShowMessage('L' + #252 + 'tfen yeni kullan' + #305 + 'c' + #305 + ' ad' + #305 + ' ve ' + #351 + 'ifre giriniz.');
    Exit;
  end;

  RestRequest.Params.Clear;
  RestRequest.Method := rmPOST;
  RestRequest.Resource := 'auth/register';

  JSONPayload := TJSONObject.Create;
  try
    JSONPayload.AddPair('username', Trim(edtUsername.Text));
    JSONPayload.AddPair('password', Trim(edtPassword.Text));
    RestRequest.AddBody(JSONPayload);
    
    try
      RestRequest.Execute;
      if RestResponse.StatusCode = 201 then
      begin
        ShowMessage('Kay' + #305 + 't Ba' + #351 + 'ar' + #305 + 'l' + #305 + '! ' + #350 + 'imdi giri' + #351 + ' yapabilirsiniz.');
        LogYaz('Yeni kullan' + #305 + 'c' + #305 + ' kaydedildi: ' + Trim(edtUsername.Text));
      end
      else
        ShowMessage('Kay' + #305 + 't ba' + #351 + 'ar' + #305 + 's' + #305 + 'z: ' + RestResponse.Content);
    except
      on E: Exception do ShowMessage('Ba' + #287 + 'lant' + #305 + ' Hatas' + #305 + ': ' + E.Message);
    end;
  finally
    RestRequest.Params.Clear;
  end;
end;

procedure TfrmMain.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  LogYaz('Sistem kapat' + #305 + 'l' + #305 + 'yor.');
  // Optionnel : arrêter python ou docker ici. 
  // Actuellement, on tue juste python pour ne pas laisser Uvicorn tourner dans le vide
  ShellExecute(0, 'open', 'taskkill.exe', '/F /IM python.exe', nil, SW_HIDE);
end;

procedure TfrmMain.GelismisAramaYap;
begin
  LogYaz('Veritaban' + #305 + ' sorgulan' + #305 + 'yor...');
  RestRequest.Params.Clear;
  RestRequest.Method := rmGET;
  RestRequest.Resource := 'search/advanced';

  if Trim(edtSehir.Text) <> '' then
    RestRequest.AddParameter('city', Trim(edtSehir.Text), TRESTRequestParameterKind.pkQUERY);
  if (Trim(cmbSektor.Text) <> '') and (cmbSektor.Text <> 'T' + #252 + 'm' + #252) then
    RestRequest.AddParameter('industry', Trim(cmbSektor.Text), TRESTRequestParameterKind.pkQUERY);
  if (Trim(edtUnvan.Text) <> '') then
    RestRequest.AddParameter('has_title', Trim(edtUnvan.Text), TRESTRequestParameterKind.pkQUERY);
  if (cmbCalisanSayisi.ItemIndex > 0) then
    RestRequest.AddParameter('min_company_size', cmbCalisanSayisi.Text, TRESTRequestParameterKind.pkQUERY);
  
  if chkSadeceYatirimAlanlar.Checked then
    RestRequest.AddParameter('has_investment', 'true', TRESTRequestParameterKind.pkQUERY);

  try
    RestRequest.Execute;
    if RestResponse.StatusCode = 200 then
    begin
      if MemTableSonuclar.Active then
        MemTableSonuclar.Close;

      RestAdapter.Active := True;

      if MemTableSonuclar.Active then
      begin
        LogYaz('Sorgu ba' + #351 + 'ar' + #305 + 'l' + #305 + ': ' + IntToStr(MemTableSonuclar.RecordCount) + ' firma listelendi.');
        
        // Fix DBGrid display to avoid showing nested '(DataSet)' objects
        dbgSonuclar.Columns.Clear;
        with dbgSonuclar.Columns.Add do begin FieldName := 'name'; Title.Caption := 'Firma Ad' + #305; Width := 220; end;
        with dbgSonuclar.Columns.Add do begin FieldName := 'industry'; Title.Caption := 'Sekt' + #246'r'; Width := 150; end;
        with dbgSonuclar.Columns.Add do begin FieldName := 'city'; Title.Caption := #350'ehir'; Width := 120; end;
        with dbgSonuclar.Columns.Add do begin FieldName := 'website'; Title.Caption := 'Web Sitesi'; Width := 200; end;
        with dbgSonuclar.Columns.Add do begin FieldName := 'confidence_score'; Title.Caption := 'G' + #252'ven(%)'; Width := 80; end;
        with dbgSonuclar.Columns.Add do begin FieldName := 'description'; Title.Caption := 'Detay'; Width := 300; end;
      end
      else
        LogYaz('Arama sonucu bo' + #351 + '.');
    end
    else
      LogYaz('Hata: HTTP ' + RestResponse.StatusCode.ToString);
  except
    on E: Exception do LogYaz('Ba' + #287 + 'lant' + #305 + ' Hatas' + #305 + ': ' + E.Message);
  end;
end;

procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  GelismisAramaYap;
end;

procedure TfrmMain.btnTaramaBaslatClick(Sender: TObject);
var
  SorguKelimeleri: string;
begin
  SorguKelimeleri := Trim(edtSehir.Text);
  if SorguKelimeleri = '' then
  begin
    if (Trim(cmbSektor.Text) <> '') and (cmbSektor.Text <> 'T' + #252 + 'm' + #252) then
      SorguKelimeleri := Trim(cmbSektor.Text)
    else
      SorguKelimeleri := 'Denizli Tekstil';
  end
  else
  begin
    if (Trim(cmbSektor.Text) <> '') and (cmbSektor.Text <> 'T' + #252 + 'm' + #252) then
      SorguKelimeleri := SorguKelimeleri + ' ' + Trim(cmbSektor.Text);
  end;

  LogYaz('OSINT veri toplama tetikleniyor: "' + SorguKelimeleri + '"');
  btnTaramaBaslat.Enabled := False;

  TTask.Run(procedure
  begin
    RestReqStats.Params.Clear;
    RestReqStats.Method := rmPOST;
    RestReqStats.Resource := 'scraper/scan';
    RestReqStats.AddParameter('query', SorguKelimeleri, TRESTRequestParameterKind.pkQUERY);

    try
      RestReqStats.Execute;
      TThread.Queue(nil, procedure
      begin
        if RestResStats.StatusCode = 202 then
        begin
          LogYaz(#304 + #351 + 'lem ba' + #351 + 'lat' + #305 + 'ld' + #305 + '! Botlar arka planda "' + SorguKelimeleri + '" i' + #231 + 'in ' + #231 + 'al' + #305 + #351 + #305 + 'yor.');
          ShowMessage('OSINT taramas' + #305 + ' ba' + #351 + 'ar' + #305 + 'yla ba' + #351 + 'lat' + #305 + 'ld' + #305 + '!' + #13#10 + 'Veriler arka planda toplanacak.');
        end
        else
          LogYaz('Hata: Tarama tetikleme ba' + #351 + 'ar' + #305 + 's' + #305 + 'z. Kod: ' + RestResStats.StatusCode.ToString);

        btnTaramaBaslat.Enabled := True;
      end);
    except
      on E: Exception do
      begin
        TThread.Queue(nil, procedure
        begin
          LogYaz('Sunucu ba' + #287 + 'lant' + #305 + ' hatas' + #305 + ': ' + E.Message);
          btnTaramaBaslat.Enabled := True;
        end);
      end;
    end;
  end);
end;

procedure TfrmMain.btnAnalizGetirClick(Sender: TObject);
var
  JSONObj, SubObj: TJSONObject;
  JSONPair, SubPair: TJSONPair;
  i, j: Integer;
begin
  LogYaz('Kapsaml' + #305 + ' istatistikler ' + #231 + 'ekiliyor...');
  mmoIstatistik.Lines.Clear;
  mmoIstatistik.Lines.Add('================================================');
  mmoIstatistik.Lines.Add('          KAPSAMLI OSINT VER' + #304 + ' RAPORU');
  mmoIstatistik.Lines.Add('================================================');
  mmoIstatistik.Lines.Add('');

  RestReqStats.Params.Clear;
  RestReqStats.Method := rmGET;
  RestReqStats.Resource := 'reports/statistics';

  try
    RestReqStats.Execute;
    if RestResStats.StatusCode = 200 then
    begin
      JSONObj := TJSONObject.ParseJSONValue(RestResStats.Content) as TJSONObject;
      if Assigned(JSONObj) then
      begin
        try
          mmoIstatistik.Lines.Add('-> Toplam Kay' + #305 + 'tl' + #305 + ' Firma: ' + JSONObj.GetValue('total_companies').Value);
          mmoIstatistik.Lines.Add('-> Toplam Tespit Edilen Yetkili: ' + JSONObj.GetValue('total_officials').Value);
          mmoIstatistik.Lines.Add('');

          // Sektörel
          mmoIstatistik.Lines.Add('--- SEKT' + #214 + 'REL DA' + #286 + 'ILIM ---');
          SubObj := JSONObj.GetValue('industry_distribution') as TJSONObject;
          if Assigned(SubObj) then
            for j := 0 to SubObj.Count - 1 do
              mmoIstatistik.Lines.Add('  [#] ' + SubObj.Pairs[j].JsonString.Value + ' : ' + SubObj.Pairs[j].JsonValue.Value);
          mmoIstatistik.Lines.Add('');

          // Bölgesel
          mmoIstatistik.Lines.Add('--- B' + #214 + 'LGESEL DA' + #286 + 'ILIM (' + #350 + 'EH' + #304 + 'R) ---');
          SubObj := JSONObj.GetValue('regional_distribution') as TJSONObject;
          if Assigned(SubObj) then
            for j := 0 to SubObj.Count - 1 do
              mmoIstatistik.Lines.Add('  [#] ' + SubObj.Pairs[j].JsonString.Value + ' : ' + SubObj.Pairs[j].JsonValue.Value);
          mmoIstatistik.Lines.Add('');

          // Unvanlar
          mmoIstatistik.Lines.Add('--- Y' + #214 + 'NET' + #304 + 'C' + #304 + ' / ' + #220 + 'NVAN DA' + #286 + 'ILIMI ---');
          SubObj := JSONObj.GetValue('title_distribution') as TJSONObject;
          if Assigned(SubObj) then
            for j := 0 to SubObj.Count - 1 do
              mmoIstatistik.Lines.Add('  [#] ' + SubObj.Pairs[j].JsonString.Value + ' : ' + SubObj.Pairs[j].JsonValue.Value);

          LogYaz('Kapsaml' + #305 + ' istatistikler ba' + #351 + 'ar' + #305 + 'yla g' + #252 + 'ncellendi.');
        finally
          JSONObj.Free;
        end;
      end
      else
        mmoIstatistik.Lines.Add('Veri format' + #305 + ' anla' + #351 + #305 + 'lamad' + #305 + '.');
    end
    else
      mmoIstatistik.Lines.Add('Analiz verisi sunucudan al' + #305 + 'nmad' + #305 + '. Kod: ' + RestResStats.StatusCode.ToString);
  except
    on E: Exception do mmoIstatistik.Lines.Add('Ba' + #287 + 'lant' + #305 + ' Hatas' + #305 + ': ' + E.Message);
  end;
end;

procedure TfrmMain.dbgSonuclarDblClick(Sender: TObject);
var
  Detay: string;
  JSONArr: TJSONArray;
  i, j: Integer;
  CompObj: TJSONObject;
  OffArr: TJSONArray;
  OffObj: TJSONObject;
  TargetID: Integer;
begin
  if not MemTableSonuclar.Active then Exit;
  if MemTableSonuclar.IsEmpty then Exit;

  TargetID := MemTableSonuclar.FieldByName('id').AsInteger;

  Detay := '==== F' + #304 + 'RMA B' + #304 + 'LG' + #304 + 'S' + #304 + ' ====' + #13#10 +
           'Firma Ad' + #305 + ': ' + MemTableSonuclar.FieldByName('name').AsString + #13#10 +
           'Sekt' + #246 + 'r: ' + MemTableSonuclar.FieldByName('industry').AsString + #13#10 +
           'Web Sitesi: ' + MemTableSonuclar.FieldByName('website').AsString + #13#10 +
           'G' + #252 + 'ven Skoru: %' + MemTableSonuclar.FieldByName('confidence_score').AsString + #13#10#13#10;

  Detay := Detay + '--- YETK' + #304 + 'L' + #304 + 'LER (Karar Vericiler) ---' + #13#10;

  try
    JSONArr := TJSONObject.ParseJSONValue(RestResponse.Content) as TJSONArray;
    if Assigned(JSONArr) then
    begin
      for i := 0 to JSONArr.Count - 1 do
      begin
        CompObj := JSONArr.Items[i] as TJSONObject;
        if CompObj.GetValue('id').Value.ToInteger = TargetID then
        begin
          OffArr := CompObj.GetValue('officials') as TJSONArray;
          if Assigned(OffArr) and (OffArr.Count > 0) then
          begin
            for j := 0 to OffArr.Count - 1 do
            begin
              OffObj := OffArr.Items[j] as TJSONObject;
              Detay := Detay + '  > ' + OffObj.GetValue('full_name').Value + ' (' + OffObj.GetValue('title').Value + ')' + #13#10;
            end;
          end
          else
            Detay := Detay + '  Yetkili bilgisi bulunamad' + #305 + '.' + #13#10;
          Break;
        end;
      end;
      JSONArr.Free;
    end;
  except
    Detay := Detay + '  Yetkili verisi JSON okuma hatas' + #305 + '.' + #13#10;
  end;

  ShowMessage(Detay);
  LogYaz(MemTableSonuclar.FieldByName('name').AsString + ' detaylar' + #305 + ' g' + #246 + 'r' + #252 + 'nt' + #252 + 'lendi.');
end;

end.
